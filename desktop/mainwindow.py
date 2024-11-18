import urllib.parse

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import QTimer, Qt, QRect, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen

from desktop.myRect import MyRect
from desktop.view.droidcam_link_dialog import DroidcamLinkDialog
from desktop.view.mainwindow import Ui_MainWindow

from desktop.video_source.droidcam import DroidcamVideoSource
from recognizer import Recognizer  # Ensure this imports correctly


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.image_label = self.ui.ImageLabel
        self.text_label = self.ui.TextLabel

        self.ui.actionVSDroidcam.triggered.connect(self.get_droidcam_link)

        self.setWindowTitle("Face Recognition App")
        # vs = DroidcamVideoSource("https://192.168.0.106:4343/video")
        vs = None
        self.recognizer = Recognizer(video_source=vs)

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

        self.marked_persons = {}

    def get_droidcam_link(self):
        dlg = DroidcamLinkDialog()
        if dlg.exec():
            text = dlg.lineEdit.text()
            vs = DroidcamVideoSource(text)
            self.recognizer.set_video_source(vs)
            print(f"Set VS to {text}")
        else:
            print("Cancelled")

    def toggle_hud(self):
        """Toggle HUD visibility."""
        self.recognizer.set_hud_visible(not self.recognizer.is_hud_visible())

    def update_frame(self):
        """Update the displayed frame."""
        self.frame = self.recognizer.get_iamge().copy()
        if self.frame is not None:
            height, width, channel = self.frame.shape
            q_img = QImage(self.frame.data, width, height, 3 * width, QImage.Format.Format_BGR888)

            self.process_recognitions()
            self.paint_rectangles(q_img)
            self.paint_recognitions(q_img)

            pixmap = QPixmap.fromImage(q_img)
            self.image_label.setFixedSize(width, height)
            self.image_label.setPixmap(pixmap)

    def process_recognitions(self):
        for p in self.recognizer.get_recognized():
            if p.score is None:
                continue

            mid_point = QPoint(p.tlwh[0] + p.tlwh[2] // 2, p.tlwh[1] + p.tlwh[3] // 2)

            if p.name in self.marked_persons:
                self.marked_persons[p.name] = p
                continue

            for rect in self.rectangles:
                if rect.contains(mid_point):
                    self.marked_persons[p.name] = p
                    break

        text = 'Marked:\n\t'
        text += '\n\t'.join(self.marked_persons.keys())
        self.text_label.setText(text)

    def paint_recognitions(self, q_img):
        # Draw rectangles on the frame copy
        painter = QPainter(q_img)

        def green():
            painter.setPen(QPen(QColor(0, 255, 0), 5))
            painter.setBrush(QColor(0, 255, 0, 0))

        def blue():
            painter.setPen(QPen(QColor(0, 0, 255), 5))
            painter.setBrush(QColor(0, 0, 255, 0))

        def purple():
            painter.setPen(QPen(QColor(255, 0, 255), 5))
            painter.setBrush(QColor(255, 0, 255, 0))

        for p in self.recognizer.get_recognized():
            green()

            if p.name in self.marked_persons:
                purple()
            else:
                mid_point = QPoint(p.tlwh[0] + p.tlwh[2] // 2, p.tlwh[1] + p.tlwh[3] // 2)
                for rect in self.rectangles:
                    if rect.contains(mid_point):
                        blue()
                        break

            person_rect = QRect(*p.tlwh)
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

        if event.button() == Qt.MouseButton.LeftButton and self.image_label.underMouse():
            mouse_pos = self.image_label.mapFromGlobal(event.globalPos())
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
        mouse_pos = self.image_label.mapFromGlobal(event.globalPos())
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

    def closeEvent(self, event):
        self.recognizer.stop()  # Ensure recognizer is stopped
        event.accept()  # Accept the event to close the window
