import copy
from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QFileDialog
from PySide6.QtCore import QTimer, Qt, QRect, QPoint
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen

from desktop.view.widget.marked_persons_widget import MarkedPersonsWidget
from desktop.myRect import MyRect
from desktop.save import Save
from desktop.video_source.camera_by_index import CameraByIndex
from desktop.view.dialog.camera_index_dialog import CameraIndexDialog
from desktop.view.dialog.droidcam_link_dialog import DroidcamLinkDialog
from desktop.view.ui.mainwindow import Ui_MainWindow

from desktop.video_source.droidcam import DroidcamVideoSource
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

        self.ui.actionVSDroidcam.triggered.connect(self.get_droidcam_link)
        self.ui.actionVSCameraByIndex.triggered.connect(self.get_camera_by_index)
        self.ui.actionSaveSave.triggered.connect(self.save_save)
        self.ui.actionLoadSave.triggered.connect(self.load_save)

        self.setWindowTitle("Face Recognition App")
        vs = DroidcamVideoSource("https://192.168.0.106:4343/video")
        # vs = None
        # vs = CameraByIndex(0)

        self.recognizer = Recognizer(video_source=vs)
        self.toggle_hud(state=False)

        # Timer to update frame
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000 // 30)  # 30 FPS

        self.frame = None
        self.recognizer.start()

        self.marked_persons_widget_dict = MarkedPersonsWidget(self)
        self.ui.StudentsListLayout.addWidget(self.marked_persons_widget_dict)

    def change_video_source(self, vs):
        path = Path('temp.rcfg')
        self.save_save(path)
        self.frame = vs.get_frame()
        self.recognizer.set_video_source(vs)
        self.load_save(path)
        path.unlink()

    def get_droidcam_link(self):
        dlg = DroidcamLinkDialog()
        if dlg.exec():
            text = dlg.lineEdit.text()
            self.change_video_source(DroidcamVideoSource(text))

    def get_camera_by_index(self):
        while True:
            dlg = CameraIndexDialog()
            if dlg.exec():
                text = dlg.lineEdit.text()
                try:
                    index = int(text)
                except ValueError:
                    continue
                self.change_video_source(CameraByIndex(index))
                break
            else:
                break

    def save_save(self, path: Path = None):
        save = Save(rectangles=self.image_rectangles_label.get_rectangles(),
                    image_height=self.frame.shape[0],
                    image_width=self.frame.shape[1])
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
            else:
                return

        rectangles = []
        x_ratio = self.frame.shape[1] / save.image_width
        y_ratio = self.frame.shape[0] / save.image_height
        for rect in save.rectangles:
            r = copy.deepcopy(rect)
            rectangles.append(MyRect(int(r.x() * x_ratio),
                                     int(r.y() * y_ratio),
                                     int(r.width() * x_ratio),
                                     int(r.height()) * y_ratio))
        self.image_rectangles_label.set_rectangles(rectangles)

    def toggle_hud(self, state=None):
        if isinstance(state, bool):
            self.recognizer.set_hud_visible(state)
        else:
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
            self.image_rectangles_label.setFixedSize(width, height)
            self.image_rectangles_label.setPixmap(pixmap)

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

    def paint_rectangles(self, q_img):
        # Draw rectangles on the frame copy
        painter = QPainter(q_img)

        for rect in self.image_rectangles_label.get_rectangles():
            rect.draw(painter)

        # Show non-yet-created rectangle while holding mouse key
        start_point, end_point = self.image_rectangles_label.get_start_end_points()
        if start_point is not None and end_point is not None:
            painter.setPen(QPen(QColor(255, 0, 0), 5))
            painter.setBrush(QColor(255, 0, 0, 90))
            painter.drawRect(QRect(start_point.x(), start_point.y(),
                                   end_point.x() - start_point.x(),
                                   end_point.y() - start_point.y()))

        painter.end()

    def closeEvent(self, event):
        if self.recognizer:
            self.recognizer.stop()  # Ensure recognizer is stopped
        event.accept()  # Accept the event to close the window
