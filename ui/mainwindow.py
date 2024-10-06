import sys
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QApplication
from PySide6.QtCore import QTimer, Qt, QRect
from recognizer import Recognizer  # Ensure this imports correctly
import cv2
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen


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
        self.label.setFixedSize(640, 480)  # Set size for the label
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
        self.rectangles = []  # To store rectangle coordinates
        self.start_point = None  # Starting point for rectangle
        self.end_point = None  # End point for rectangle

        self.frame = None
        self.recognizer.start()

    def toggle_hud(self):
        """Toggle HUD visibility."""
        self.recognizer.set_hud_visible(not self.recognizer.hud_visible)

    def update_frame(self):
        """Update the displayed frame."""
        self.frame = self.recognizer.tracking_image
        if self.frame is not None:
            self.frame = self.frame.copy()
            height, width, channel = self.frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(self.frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)

            # Draw rectangles on the frame copy
            painter = QPainter(q_img)
            painter.setPen(QPen(QColor(255, 0, 0, 128), 5))  # Red with alpha
            painter.setBrush(QColor(255, 0, 0, 90))  # Transparent fill
            for rect in self.rectangles:
                painter.drawRect(rect)
            painter.end()

            pixmap = QPixmap.fromImage(q_img)
            self.label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.rectangles:
                self.rectangles.pop()  # Remove the last rectangle

    def mousePressEvent(self, event):
        """Capture the starting point of the rectangle."""
        if event.button() == Qt.MouseButton.LeftButton and self.label.underMouse():
            # Get mouse position relative to the label
            mouse_x = event.pos().x() - self.label.pos().x()
            mouse_y = event.pos().y() - self.label.pos().y()
            print('Left down at:', mouse_x, mouse_y)
            self.start_point = (mouse_x, mouse_y)
            self.end_point = None  # Reset end point

    def mouseMoveEvent(self, event):
        """Capture the end point of the rectangle while dragging."""
        if self.start_point is not None and self.label.underMouse():
            mouse_x = event.pos().x() - self.label.pos().x()
            mouse_y = event.pos().y() - self.label.pos().y()
            self.end_point = (mouse_x, mouse_y)

    def mouseReleaseEvent(self, event):
        """Finalize the rectangle and add it to the list."""
        if event.button() == Qt.MouseButton.LeftButton and self.start_point and self.end_point:
            print('Left up at:', self.end_point)
            # Create a QRect from the start and end points
            rect = QRect(self.start_point[0], self.start_point[1],
                         self.end_point[0] - self.start_point[0],
                         self.end_point[1] - self.start_point[1])
            self.rectangles.append(rect)  # Add the rectangle to the list
            self.start_point = None  # Reset start point
            self.end_point = None  # Reset end point

    def closeEvent(self, event):
        self.recognizer.stop()  # Ensure recognizer is stopped
        event.accept()  # Accept the event to close the window
