import os
import sys
from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets

from src.common import config
from src.presentation.app import App


if __name__ == "__main__":
    # Create a QApplication object to manage the GUI application
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QGroupBox {
            border: 1px solid #c0c0c0;
            border-radius: 8px;
            margin-top: 12px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            color: #4CAF50;
            font-size: 16px;
            font-weight: bold;
            padding: 0 3px;
        }
    """)

    app.setWindowIcon(QIcon(os.path.join(config.icon_dir, 'facebook.png')))

    # Create the main window
    MainWindow = QtWidgets.QMainWindow()

    # Create an instance of the GUI class
    ui = App()

    # Set up the user interface defined in the GUI class
    ui.setupUi(MainWindow)

    # Show the main window
    MainWindow.show()

    # Start the application event loop
    sys.exit(app.exec())
