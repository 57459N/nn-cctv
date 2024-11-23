from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel

from desktop.myRect import MyRect


class RectanglesLabelList(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Selected zones
        self.rectangles: list[MyRect] = []  # To store rectangle coordinates
        self.start_point = None  # Starting point for rectangle
        self.end_point = None  # End point for rectangle
        self.resizing_rect = None
        self.resize_direction = None  # Determines which corner to resize

    def get_rectangles(self):
        return self.rectangles

    def set_rectangles(self, rectangles: list[MyRect]):
        self.rectangles = rectangles

    def get_start_end_points(self):
        return self.start_point, self.end_point

    def pop_last_rect(self):
        if self.rectangles:
            self.rectangles.pop()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.pop_last_rect()

    def mousePressEvent(self, event):
        """Capture the starting point of the rectangle."""

        if event.button() == Qt.MouseButton.LeftButton and self.underMouse():
            mouse_pos = self.mapFromGlobal(event.globalPos())
            for i, rect in enumerate(self.rectangles):
                corner, direction = self.is_pos_near_corner(mouse_pos, rect)
                if corner:
                    self.resizing_rect = i
                    self.resize_direction = direction
                    return
            self.start_point = mouse_pos
            self.end_point = None  # Reset end point

    def mouseMoveEvent(self, event):
        """Capture the end point of the rectangle while dragging or resizing."""
        mouse_pos = self.mapFromGlobal(event.globalPos())
        if self.resizing_rect is not None:
            rect = self.rectangles[self.resizing_rect]
            if 'top' in self.resize_direction:
                rect.setTop(mouse_pos.y())
            if 'bottom' in self.resize_direction:
                rect.setBottom(mouse_pos.y())
            if 'left' in self.resize_direction:
                rect.setLeft(mouse_pos.x())
            if 'right' in self.resize_direction:
                rect.setRight(mouse_pos.x())
        elif self.start_point is not None:
            self.end_point = mouse_pos

    def mouseReleaseEvent(self, event):
        """Finalize the rectangle and add it to the list."""
        if self.resizing_rect is not None:
            self.resizing_rect = None  # Stop resizing
        elif event.button() == Qt.MouseButton.LeftButton and self.start_point and self.end_point:
            rect = MyRect(self.start_point.x(), self.start_point.y(),
                          self.end_point.x() - self.start_point.x(),
                          self.end_point.y() - self.start_point.y())
            self.rectangles.append(rect)  # Add the rectangle to the list
            self.start_point = None
            self.end_point = None

    @staticmethod
    def is_pos_near_corner(pos, rect, margin=10):
        """Check if the mouse position is near a corner for resizing."""
        corners = rect.get_rect_corners()
        directions = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        for corner, direction in zip(corners, directions):
            if abs(corner.x() - pos.x()) <= margin and abs(corner.y() - pos.y()) <= margin:
                return corner, direction
        return None, None
