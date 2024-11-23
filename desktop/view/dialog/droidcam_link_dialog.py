from PySide6.QtGui import Qt
from PySide6.QtWidgets import QDialogButtonBox, QLineEdit, QLabel, QDialog, QVBoxLayout


class DroidcamLinkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Droidcam Link")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.resize(300, 100)

        self.label = QLabel("Enter the IP address of the Droidcam device:")
        self.lineEdit = QLineEdit()
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
