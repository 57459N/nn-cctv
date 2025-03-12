import copy
from pathlib import Path

import cv2
from PySide6.QtWidgets import QMainWindow, QFileDialog
from PySide6.QtCore import QTimer, Qt, QRect, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen

from desktop.view.dialog.scale_dialog import ScaleDialog
from desktop.view.widget.marked_persons_widget import MarkedPersonsWidget
from desktop.myRect import MyRect
from desktop.save import Save
from desktop.video_source.camera_by_index import CameraByIndex
from desktop.view.dialog.camera_index_dialog import CameraIndexDialog
from desktop.view.dialog.network_url_dialog import NetworkUrlDialog
from desktop.view.ui.mainwindow import Ui_MainWindow

from desktop.video_source.network import NetworkVideoSource
from desktop.view.widget.rectangles_list_label import RectanglesLabelList
from recognizer import Recognizer  # Ensure this imports correctly


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.image_rectangles_label = RectanglesLabelList(self)
        self.ui.MainHLayout.insertWidget(0, self.image_rectangles_label)

        self.text_label = self.ui.TextLabel

        self.ui.actionVSDroidcam.triggered.connect(self.get_network_url)
        self.ui.actionVSCameraByIndex.triggered.connect(self.get_camera_by_index)
        self.ui.actionSaveSave.triggered.connect(self.save_save)
        self.ui.actionLoadSave.triggered.connect(self.load_save)
        self.ui.actionToggleHUD.triggered.connect(self.toggle_hud)
        self.ui.actionScaleVideo.triggered.connect(self.scale)

        self.setWindowTitle("Face Recognition App")
        # vs = DroidcamVideoSource("https://192.168.0.106:4343/video")
        # vs = DroidcamVideoSource("rtsp://admin:@192.168.0.69:554")
        # vs = None
        vs = CameraByIndex(0)

        self.recognizer = Recognizer(video_source=vs)

        # Timer to update frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // 30)  # 30 FPS

        self.frame = None
        self.scale_factor: float = 1

        self.recognizer.start()

        self.marked_persons_widget_dict = MarkedPersonsWidget(self)
        self.ui.StudentsListLayout.addWidget(self.marked_persons_widget_dict)

    def get_network_url(self):
        dlg = NetworkUrlDialog()
        if dlg.exec():
            text = dlg.lineEdit.text()
            self.recognizer.set_video_source(NetworkVideoSource(text))

    def get_camera_by_index(self):
        while True:
            dlg = CameraIndexDialog()
            if dlg.exec():
                text = dlg.lineEdit.text()
                try:
                    index = int(text)
                except ValueError:
                    continue
                self.recognizer.set_video_source(CameraByIndex(index))
                break
            else:
                break

    def scale(self):
        while True:
            dlg = ScaleDialog(default_value=str(self.scale_factor))

            if not dlg.exec_():
                break
            try:
                new_scale = float(dlg.lineEdit.text())
            except ValueError:
                continue
            self.scale_factor = new_scale
            break

    def save_save(self, path: Path = None):
        save = Save(src=self.recognizer.get_video_source().src,
                    rectangles=self.image_rectangles_label.get_rectangles(),
                    is_hud_visible=self.recognizer.is_hud_visible(),
                    scale_factor=self.scale_factor)
        if path:
            save.save(path)
        else:
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setAcceptMode(QFileDialog.AcceptSave)
            if dlg.exec():
                save.save(Path(dlg.selectedFiles()[0]).with_suffix('.rcfg'))

    def load_save(self, path: Path = None):
        if path:
            save = Save.load(path)
        else:
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.AnyFile)
            dlg.setAcceptMode(QFileDialog.AcceptOpen)
            if dlg.exec():
                save = Save.load(Path(dlg.selectedFiles()[0]))
                dlg.close()
            else:
                return

        if isinstance(save.src, int):
            source_type = CameraByIndex
        elif isinstance(save.src, str):
            source_type = NetworkVideoSource
        else:
            assert False, 'Invalid source type'

        self.recognizer.set_video_source(source_type(save.src))
        self.image_rectangles_label.set_rectangles(save.rectangles)
        self.recognizer.set_hud_visible(save.is_hud_visible)
        self.scale_factor = save.scale_factor

    # def scale_rectangles(self, x_ratio: float, y_ratio: float):

    def toggle_hud(self):
        self.recognizer.set_hud_visible(not self.recognizer.is_hud_visible())

    def update_frame(self):
        """Update the displayed frame."""
        self.frame = self.recognizer.get_iamge().copy()
        if self.frame is not None:
            height, width, channel = self.frame.shape
            q_img = QImage(self.frame.data, width, height, 3 * width, QImage.Format.Format_BGR888)

            self.process_recognitions()
            self.paint_recognitions(q_img)
            self.image_rectangles_label.set_image(q_img)
            self.image_rectangles_label.scale(self.scale_factor)
            self.image_rectangles_label.show_image()

    def process_recognitions(self):
        for p in self.recognizer.get_recognized():
            if p.score is None:
                continue

            mid_point = QPoint(p.tlwh[0] + p.tlwh[2] // 2, p.tlwh[1] + p.tlwh[3] // 2)

            if p.name in self.marked_persons_widget_dict:
                self.marked_persons_widget_dict.update_person(p)
                continue

            for rect in self.image_rectangles_label.get_rectangles():
                if rect.contains(mid_point) and not p.is_unknown:
                    self.marked_persons_widget_dict.add_person(p)
                    break

    def paint_recognitions(self, q_img):
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

        def red():
            painter.setPen(QPen(QColor(255, 0, 0), 5))
            painter.setBrush(QColor(255, 0, 0, 0))

        for p in self.recognizer.get_recognized():
            green()

            if p.name in self.marked_persons_widget_dict:
                purple()
            else:
                mid_point = QPoint(p.tlwh[0] + p.tlwh[2] // 2, p.tlwh[1] + p.tlwh[3] // 2)
                for rect in self.image_rectangles_label.get_rectangles():
                    if rect.contains(mid_point):
                        blue()
                        break

            if p.is_unknown:
                red()

            person_rect = QRect(*p.tlwh)
            painter.drawRect(person_rect)

        painter.end()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.image_rectangles_label.pop_last_rect()

    def closeEvent(self, event):
        if self.recognizer:
            self.recognizer.stop()  # Ensure recognizer is stopped
        event.accept()  # Accept the event to close the window
