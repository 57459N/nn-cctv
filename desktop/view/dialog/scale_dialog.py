from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QLabel, QDialogButtonBox, QVBoxLayout, QHBoxLayout


class ScaleDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, default_value: str = ''):
        super().__init__(parent)
        self.setWindowTitle("Camera by index")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.resize(300, 100)

        self.label = QLabel("Enter new scale ratio of video:")
        self.lineEdit = QLineEdit()
        self.lineEdit.setText(default_value)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
