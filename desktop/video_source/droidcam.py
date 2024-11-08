import cv2

from desktop.video_source.base import VideoSource


class DroidcamVideoSource(VideoSource):
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(url)

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame

    def __del__(self):
        self.cap.release()
