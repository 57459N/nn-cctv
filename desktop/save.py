import pickle

from desktop.myRect import MyRect


class Save:
    def __init__(self, rectangles: list[MyRect], image_width: int, image_height: int, is_hud_visible: bool = False):
        self.rectangles = rectangles
        self.image_width = image_width
        self.image_height = image_height
        self.is_hud_visible = is_hud_visible

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
