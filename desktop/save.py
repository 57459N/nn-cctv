from dataclasses import dataclass


@dataclass
class Save:
    rectangles: list[int] = None
    image_width: int = 0
    image_height: int = 0
