import pickle

from desktop.myRect import MyRect
from desktop.video_source.base import VideoSource


class Save:
    def __init__(self, src, rectangles: list[MyRect], is_hud_visible: bool = False, scale_factor: float = 1):
        self.src = src
        self.rectangles = rectangles
        self.is_hud_visible = is_hud_visible
        self.scale_factor = scale_factor

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            try:
                obj: object = pickle.load(f)
                return Save(**obj.__dict__)
            except Exception as e:
                print(e)
