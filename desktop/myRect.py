from typing import Any

from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QPen, QPainter


class MyRect(QRect):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.color = QColor(0, 0, 0)
        self.type: Any = None

    def draw(self, painter: QPainter):
        pen = painter.pen()
        brush = painter.brush()

        painter.setPen(QPen(QColor(255, 0, 0, 128), 5))  # Red with alpha
        painter.setBrush(QColor(255, 0, 0, 90))  # Transparent fill
        painter.drawRect(self)

        # Draw corner handles for resizing
        for corner in self.get_rect_corners():
            painter.setBrush(QColor(255, 0, 0))
            painter.drawRect(corner.x() - 5, corner.y() - 5, 10, 10)
            painter.setBrush(QColor(255, 0, 0, 90))  # recover the brush

        painter.setPen(pen)
        painter.setBrush(brush)

    def __str__(self):
        return f"({self.x()}, {self.y()}, {self.width()}, {self.height()})"

    def get_rect_corners(self):
        return [
            self.topLeft(),
            self.topRight(),
            self.bottomLeft(),
            self.bottomRight()
        ]
