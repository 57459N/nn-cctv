import sys

import numpy as np
from PySide6 import QtGui
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QApplication
from PySide6.QtCore import QTimer, Qt, QRect, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen

from recognizer import Recognizer  # Ensure this imports correctly
import cv2

from ui.myRect import MyRect


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Recognition App")
        self.recognizer = Recognizer()

        # Toggle button for HUD visibility
        self.hud_button = QPushButton("Toggle HUD", self)
        self.hud_button.clicked.connect(self.toggle_hud)

        # QLabel for displaying frames
        self.label = QLabel(self)
        self.label.setFixedSize(800, 600)  # Set size for the label
        self.label.setMouseTracking(True)  # Enable mouse tracking

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.hud_button)
        layout.addWidget(self.label)

        self.container = QWidget()
        self.container.setLayout(layout)
        self.setCentralWidget(self.container)

        # Timer to update frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // 30)  # 30 FPS

        # Selected zones
        self.rectangles: list[MyRect] = []  # To store rectangle coordinates
        self.start_point = None  # Starting point for rectangle
        self.end_point = None  # End point for rectangle
        self.resizing_rect = None
        self.resize_direction = None  # Determines which corner to resize

        self.frame = None
        self.recognizer.start()

    def toggle_hud(self):
        """Toggle HUD visibility."""
        self.recognizer.set_hud_visible(not self.recognizer.is_hud_visible())

    def update_frame(self):
        """Update the displayed frame."""
        self.frame = self.recognizer.tracking_image.copy()
        if self.frame is not None:
            height, width, channel = self.frame.shape
            q_img = QImage(self.frame.data, width, height, 3 * width, QImage.Format.Format_BGR888)

            self.paint_rectangles(q_img)

            self.paint_recognitions(q_img)

            pixmap = QPixmap.fromImage(q_img)
            self.label.setFixedSize(width, height)
            self.label.setPixmap(pixmap)

    def paint_recognitions(self, q_img):
        # Draw rectangles on the frame copy
        painter = QPainter(q_img)

        def green():
            painter.setPen(QPen(QColor(0, 255, 0), 5))
            painter.setBrush(QColor(0, 255, 0, 0))

        def blue():
            painter.setPen(QPen(QColor(0, 0, 255), 5))
            painter.setBrush(QColor(0, 0, 255, 90))

        for p in self.recognizer.get_recognized():
            green()
            person_rect = QRect(*p.tlwh)
            mid_point = QPoint(p.tlwh[0] + p.tlwh[2] // 2, p.tlwh[1] + p.tlwh[3] // 2)
            for rect in self.rectangles:
                if rect.contains(mid_point):
                    blue()
                    break
            painter.drawRect(person_rect)

        painter.end()

    def paint_rectangles(self, q_img):
        # Draw rectangles on the frame copy
        painter = QPainter(q_img)

        for rect in self.rectangles:
            rect.draw(painter)

        # Show non-yet-created rectangle while holding mouse key
        if self.start_point is not None and self.end_point is not None:
            painter.setPen(QPen(QColor(255, 0, 0), 5))
            painter.setBrush(QColor(255, 0, 0, 90))
            painter.drawRect(QRect(self.start_point.x(), self.start_point.y(),
                                   self.end_point.x() - self.start_point.x(),
                                   self.end_point.y() - self.start_point.y()))

        painter.end()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.rectangles:
                self.rectangles.pop()  # Remove the last rectangle

    def mousePressEvent(self, event):
        """Capture the starting point of the rectangle."""
        if event.button() == Qt.MouseButton.LeftButton and self.label.underMouse():
            mouse_pos = self.get_mouse_position(event)
            for i, rect in enumerate(self.rectangles):
                corner, direction = self.is_near_corner(rect, mouse_pos)
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
            self.start_point = None
            self.end_point = None

    def get_mouse_position(self, event):
        """Get mouse position relative to the QLabel."""
        return QPoint(event.pos().x() - self.label.pos().x(), event.pos().y() - self.label.pos().y())

    def get_rect_corners(self, rect):
        """Get the four corners of a rectangle."""
        return [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight()
        ]

    def is_near_corner(self, rect, pos, margin=10):
        """Check if the mouse position is near a corner for resizing."""
        corners = self.get_rect_corners(rect)
        directions = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        for corner, direction in zip(corners, directions):
            if (abs(corner.x() - pos.x()) <= margin and abs(corner.y() - pos.y()) <= margin):
                return corner, direction
        return None, None

    def closeEvent(self, event):
        self.recognizer.stop()  # Ensure recognizer is stopped
        event.accept()  # Accept the event to close the window
