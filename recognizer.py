import dataclasses
import threading
import time

import cv2
import numpy as np
import torch
import yaml
from torchvision import transforms

from face_alignment.alignment import norm_crop
from face_detection.scrfd.detector import SCRFD
from face_detection.yolov5_face.detector import Yolov5Face
from face_recognition.arcface.model import iresnet_inference
from face_recognition.arcface.utils import compare_encodings, read_features
from face_tracking.tracker.byte_tracker import BYTETracker
from face_tracking.tracker.visualize import plot_tracking


@dataclasses.dataclass
class Person:
    name: str
    tlwh: np.ndarray
    score: float

    def __str__(self):
        return f"{self.name} {self.score} {self.tlwh}"


class Recognizer:
    def __init__(self, droidcam_url: str = "https://192.168.0.106:4343/video",
                 tracking_config_file: str = "face_tracking/config/config_tracking.yaml",
                 hud_visible=True):

        self.droidcam_url = droidcam_url
        self.tracking_config = self.load_config(tracking_config_file)
        self.hud_visible = hud_visible

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.device = torch.device('cpu')

        self.detector = SCRFD(model_file="face_detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")
        # self.detector = Yolov5Face(model_file="face_detection/yolov5_face/weights/yolov5n-face.pt")

        self.recognizer = iresnet_inference(
            model_name="r100", path="face_recognition/arcface/weights/arcface_r100.pth", device=self.device
        )

        self.tracker = BYTETracker(args=self.tracking_config, frame_rate=30)

        self.images_names, self.images_embs = read_features(feature_path="datasets/face_features/feature")
        self.id_face_mapping = {}
        self.data_mapping = {
            "raw_image": [],
            "tracking_ids": [],
            "detection_bboxes": [],
            "detection_landmarks": [],
            "tracking_bboxes": [],
        }

        self.cap = cv2.VideoCapture(self.droidcam_url)
        self.tracking_image = None
        self.is_running = False
        self.tracking_thread = None
        self.recognition_thread = None

        self.recognized_persons: list[Person] = []

    def get_recognized(self):
        return self.recognized_persons

    def is_hud_visible(self):
        return self.hud_visible

    def get_iamge(self):
        return self.tracking_image

    def set_hud_visible(self, visible):
        """Set HUD visibility."""
        self.hud_visible = visible

    def load_config(self, file_name):
        """Load YAML config."""
        with open(file_name, "r") as stream:
            return yaml.safe_load(stream)

    def process_tracking(self, frame, frame_id, fps):
        """
        Process tracking for a frame.

        Args:
            frame: The input frame.
            frame_id (int): The frame ID.
            fps (float): Frames per second.

        Returns:
            numpy.ndarray: The processed tracking image.
        """
        # Face detection and tracking
        outputs, img_info, bboxes, landmarks = self.detector.detect_tracking(image=frame)

        tracking_tlwhs = []
        tracking_ids = []
        tracking_scores = []
        tracking_bboxes = []

        tracking_image = img_info["raw_img"]
        if outputs is not None:
            online_targets = self.tracker.update(
                outputs, [img_info["height"], img_info["width"]], (128, 128)
            )

            for i in range(len(online_targets)):
                t = online_targets[i]
                tlwh = t.tlwh
                tid = t.track_id
                vertical = tlwh[2] / tlwh[3] > self.tracking_config["aspect_ratio_thresh"]
                if tlwh[2] * tlwh[3] > self.tracking_config["min_box_area"] and not vertical:
                    x1, y1, w, h = tlwh
                    tracking_bboxes.append([x1, y1, x1 + w, y1 + h])
                    tracking_tlwhs.append(tlwh)
                    tracking_ids.append(tid)
                    tracking_scores.append(t.score)

            recs = []
            for i, tlwh in enumerate(tracking_tlwhs):
                obj_id = int(tracking_ids[i])
                name = None
                score = None
                if obj_id in self.id_face_mapping:
                    name, score = self.id_face_mapping[obj_id].split(":")
                recs.append(Person(name, np.array(tlwh), score))

            self.recognized_persons = recs

            if self.hud_visible:
                tracking_image = plot_tracking(
                    tracking_image,
                    tracking_tlwhs,
                    tracking_ids,
                    names=self.id_face_mapping,
                    frame_id=frame_id + 1,
                    fps=fps,
                )

        self.data_mapping["raw_image"] = img_info["raw_img"]
        self.data_mapping["detection_bboxes"] = bboxes
        self.data_mapping["detection_landmarks"] = landmarks
        self.data_mapping["tracking_ids"] = tracking_ids
        self.data_mapping["tracking_bboxes"] = tracking_bboxes

        return tracking_image

    @torch.no_grad()
    def get_feature(self, face_image):
        """
        Extract features from a face image.

        Args:
            face_image: The input face image.

        Returns:
            numpy.ndarray: The extracted features.
        """
        face_preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Resize((112, 112)),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            ]
        )

        # Convert to RGB
        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

        # Preprocess image (BGR)
        face_image = face_preprocess(face_image).unsqueeze(0).to(self.device)

        # Inference to get feature
        emb_img_face = self.recognizer(face_image).cpu().numpy()

        # Convert to array
        images_emb = emb_img_face / np.linalg.norm(emb_img_face)

        return images_emb

    def recognize(self):
        """Face recognition in a separate thread."""
        while self.is_running:
            raw_image = self.data_mapping["raw_image"]
            detection_landmarks = self.data_mapping["detection_landmarks"]
            detection_bboxes = self.data_mapping["detection_bboxes"]
            tracking_ids = self.data_mapping["tracking_ids"]
            tracking_bboxes = self.data_mapping["tracking_bboxes"]


            for i in range(len(tracking_bboxes)):
                for j in range(len(detection_bboxes)):
                    mapping_score = self.mapping_bbox(box1=tracking_bboxes[i], box2=detection_bboxes[j])
                    if mapping_score > 0.9:
                        face_alignment = norm_crop(img=raw_image, landmark=detection_landmarks[j])

                        score, name = self.recognition(face_image=face_alignment)
                        if name is not None:
                            if score < 0.25:
                                caption = "UN_KNOWN"
                            else:
                                caption = f"{name}:{score:.2f}"
                        else:
                            continue

                        self.id_face_mapping[tracking_ids[i]] = caption

                        detection_bboxes = np.delete(detection_bboxes, j, axis=0)
                        detection_landmarks = np.delete(detection_landmarks, j, axis=0)

                        break

            if tracking_bboxes == []:
                time.sleep(0.05)

    def recognition(self, face_image):
        """
        Recognize a face image.

        Args:
            face_image: The input face image.

        Returns:
            tuple: A tuple containing the recognition score and name.
        """
        # Get feature from face
        query_emb = self.get_feature(face_image)

        score, id_min = compare_encodings(query_emb, self.images_embs)
        name = self.images_names[id_min]
        score = score[0]

        return score, name

    def mapping_bbox(self, box1, box2):
        """
        Calculate the Intersection over Union (IoU) between two bounding boxes.

        Args:
            box1 (tuple): The first bounding box (x_min, y_min, x_max, y_max).
            box2 (tuple): The second bounding box (x_min, y_min, x_max, y_max).

        Returns:
            float: The IoU score.
        """
        # Calculate the intersection area
        x_min_inter = max(box1[0], box2[0])
        y_min_inter = max(box1[1], box2[1])
        x_max_inter = min(box1[2], box2[2])
        y_max_inter = min(box1[3], box2[3])

        intersection_area = max(0, x_max_inter - x_min_inter + 1) * max(
            0, y_max_inter - y_min_inter + 1
        )

        # Calculate the area of each bounding box
        area_box1 = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
        area_box2 = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)

        # Calculate the union area
        union_area = area_box1 + area_box2 - intersection_area

        # Calculate IoU
        iou = intersection_area / union_area

        return iou

    def tracking(self):
        """
        Face tracking in a separate thread.
        """
        # Initialize variables for measuring frame rate
        start_time = time.time_ns()
        frame_count = 0
        fps = -1

        # Initialize a tracker and a timer
        frame_id = 0

        while self.is_running:
            # todo uncomment
            _, img = self.cap.read()
            # img = np.ones((900, 1600, 3), dtype=np.uint8) * 255

            self.tracking_image = self.process_tracking(img, frame_id, fps)

            # Calculate and display the frame rate
            frame_count += 1
            if frame_count >= 30:
                fps = 1e9 * frame_count / (time.time_ns() - start_time)
                frame_count = 0
                start_time = time.time_ns()

    def start(self):
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self.tracking).start()
        self.recognition_thread = threading.Thread(target=self.recognize).start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.tracking_thread is not None:
                self.tracking_thread.join()
            if self.recognition_thread is not None:
                self.recognition_thread.join()

    def __del__(self):
        self.stop()
        if self.cap is not None:
            self.cap.release()

# Usage Example:
# recognizer = Recognizer()
# recognizer.start_tracking(droidcam_url="https://192.168.0.106:4343/video", config_file="face_tracking/config/config_tracking.yaml")
