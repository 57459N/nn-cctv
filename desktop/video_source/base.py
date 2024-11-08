from abc import abstractmethod


class VideoSource:
    @abstractmethod
    def get_frame(self):
        raise NotImplemented
