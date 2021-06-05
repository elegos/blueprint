from src.settings import Settings
import sys
from typing import Optional

from PySide6.QtWidgets import QApplication

from src.ui.mainwindow.mainwindow import MainWindow

if __name__ == "__main__":
    projectFile: Optional[str] = sys.argv[1] if len(sys.argv) > 1 else None

    # TODO: load from settings file
    settings = Settings()

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    widget = MainWindow(settings=settings)
    widget.show()

    widget.signals.closed.connect(lambda: app.quit())
    sys.exit(app.exec())
