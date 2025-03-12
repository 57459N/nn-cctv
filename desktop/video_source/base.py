from abc import abstractmethod


class VideoSource:
    def __init__(self, src):
        self.src = src
    @abstractmethod
    def get_frame(self):
        raise NotImplemented
