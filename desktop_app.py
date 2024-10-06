import sys
import threading
import time

import cv2
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap, QImage

from face_detection.scrfd.detector import SCRFD
from face_recognition.arcface.utils import read_features
from face_tracking.tracker.byte_tracker import BYTETracker
from recognize import load_config, recognize, process_tracking

detector = SCRFD(model_file="face_detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")

config_path = 'face_tracking/config/config_tracking.yaml'
config_tracking = load_config(config_path)

images_names, images_embs = read_features(feature_path=f"datasets/face_features/feature")

# Mapping of face IDs to names
id_face_mapping = {}

# Data mapping for tracking information
data_mapping = {
    "raw_image": [],
    "tracking_ids": [],
    "detection_bboxes": [],
    "detection_landmarks": [],
    "tracking_bboxes": [],
}


# Example get_frame function that returns a QImage (this is just a placeholder)
def get_frame():
    # Replace this with actual frame fetching logic
    width, height = 640, 480
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xff0000)  # Fill with red (as an example)
    return image


class FrameDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Frame Display")

        # Set up the QLabel to show frames
        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Set up the timer to call update_frame in an infinite loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms interval ~ 33fps

        # Initialize variables for measuring frame rate
        self.start_time = time.time_ns()
        self.frame_count = 0
        self.fps = -1

        # Initialize a tracker and a timer
        self.tracker = BYTETracker(args=config_tracking, frame_rate=30)
        self.frame_id = 0

        droidcam_url = 'https://192.168.0.106:4343/video'
        self.cap = cv2.VideoCapture(droidcam_url)

    def update_frame(self):
        # Get the frame from get_frame function
        _, img = self.cap.read()

        tracking_image = process_tracking(img, detector, self.tracker, config_tracking, self.frame_id, self.fps)

        # Calculate and display the frame rate
        self.frame_count += 1
        if self.frame_count >= 30:
            self.fps = 1e9 * self.frame_count / (time.time_ns() - self.start_time)
            self.frame_count = 0
            self.start_time = time.time_ns()

        height, width, channel = tracking_image.shape
        tracking_image = cv2.cvtColor(tracking_image, cv2.COLOR_BGR2RGB)
        bytesPerLine = 3 * width
        qImg = QImage(tracking_image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)

        # Convert QImage to QPixmap and display it
        pixmap = QPixmap.fromImage(qImg)
        self.label.setPixmap(pixmap)


def main():

    # Start recognition thread
    thread_recognize = threading.Thread(target=recognize)
    thread_recognize.start()

    app = QApplication(sys.argv)
    window = FrameDisplay()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
