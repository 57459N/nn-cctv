import cv2

from desktop.video_source.base import VideoSource


class CameraByIndex(VideoSource):
    def __init__(self, index):
        super().__init__(index)
        self._cap = cv2.VideoCapture(index)

    def get_frame(self):
        ret, frame = self._cap.read()
        return frame

    def __del__(self):
        self._cap.release()
