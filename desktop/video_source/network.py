import cv2

from desktop.video_source.base import VideoSource


class NetworkVideoSource(VideoSource):
    def __init__(self, url):
        super().__init__(url)
        self._cap = cv2.VideoCapture(url)

    def get_frame(self):
        ret, frame = self._cap.read()
        return frame

    def __del__(self):
        self._cap.release()
