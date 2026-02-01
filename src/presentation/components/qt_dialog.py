from PyQt6.QtWidgets import QMessageBox


class QtDialog(QMessageBox):

    def __init__(self, message, title="Notification", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Information)
        self.addButton(QMessageBox.StandardButton.Ok)
