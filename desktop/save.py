import pickle

from desktop.myRect import MyRect


class Save:
    def __init__(self, rectangles: list[MyRect], image_width: int, image_height: int):
        self.rectangles = rectangles
        self.image_width = image_width
        self.image_height = image_height

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)
