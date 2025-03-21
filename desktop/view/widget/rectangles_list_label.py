from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QImage, QPixmap
from PySide6.QtWidgets import QWidget, QLabel

from desktop.myRect import MyRect


class RectanglesLabelList(QLabel):
    rectangles_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Selected zones
        self.image = QImage()
        self.rectangles: list[MyRect] = []  # To store rectangle coordinates
        self.start_point = None  # Starting point for rectangle
        self.end_point = None  # End point for rectangle
        self.resizing_rect = None
        self.resize_direction = None  # Determines which corner to resize
        self.scale_factor = 0


    def set_image(self, image: QImage):
        self.image = image
        self.paint_rectangles(self.image)

    def show_image(self):
        pixmap = QPixmap.fromImage(self.image)
        self.setFixedSize(self.image.width(), self.image.height())
        self.setPixmap(pixmap)

    def paint_rectangles(self, q_img):
        painter = QPainter(q_img)
        painter.setPen(QPen(QColor(255, 0, 0), 5))
        painter.setBrush(QColor(255, 0, 0, 90))

        for rect in self.rectangles:
            rect.draw(painter)

        # Show non-yet-created rectangle while holding mouse key
        start, end = self.start_point, self.end_point
        if start is not None and end is not None:
            painter.drawRect(QRect(start.x(), start.y(),
                                   end.x() - start.x(),
                                   end.y() - start.y()))

        painter.end()

    def scale(self, factor: float):
        self.scale_factor = factor
        self.image = self.image.scaled(int(self.image.width() * factor), int(self.image.height() * factor))

    def get_rectangles(self):
        return self.rectangles

    def get_tlwhs(self):
        res = []
        for r in self.rectangles:
            x = r.x() if r.width() >= 0 else r.x() + r.width()
            y = r.y() if r.height() >= 0 else r.y() + r.height()
            w = abs(r.width())
            h = abs(r.height())
            res.append((x, y, w, h))
        return res

    def set_rectangles(self, rectangles: list[MyRect]):
        self.rectangles = rectangles

    def get_start_end_points(self):
        return self.start_point, self.end_point

    def pop_last_rect(self):
        if self.rectangles:
            self.rectangles.pop()
            self.rectangles_changed.emit()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.pop_last_rect()

    def get_mouse_position(self, event):
        mouse_pos = self.mapFromGlobal(event.globalPos())
        mouse_pos.setX(mouse_pos.x() / self.scale_factor)
        mouse_pos.setY(mouse_pos.y() / self.scale_factor)
        return mouse_pos

    def mousePressEvent(self, event):
        """Capture the starting point of the rectangle."""

        if event.button() == Qt.MouseButton.LeftButton and self.underMouse():
            mouse_pos = self.get_mouse_position(event)
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
        mouse_pos = self.get_mouse_position(event)
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
            self.rectangles_changed.emit()
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
