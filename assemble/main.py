# assemble/main.py - Application entry point

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from assemble.app import MainWindow

__version__ = "0.1.0"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    if "--version" in sys.argv or "-V" in sys.argv:
        print(f"ASSEMBLE {__version__}")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setApplicationName("ASSEMBLE")
    app.setOrganizationName("Fragillidae Software")

    icon_path = resource_path(os.path.join("images", "assemble_icon.png"))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
