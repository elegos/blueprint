# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class MainWindow(QMainWindow):
    ui: QWidget

    def __init__(self) -> None:
        super(MainWindow, self).__init__()
        self.load_ui()

    def load_ui(self) -> None:
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / 'form.ui')
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

    def show(self) -> None:
        return self.ui.show()


if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
