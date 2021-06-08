import argparse
import logging
import sys
from typing import Optional

from PySide6.QtWidgets import QApplication

from src.settings import Settings, SettingsManager
from src.ui.mainwindow.mainwindow import MainWindow

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log-level', help='DEBUG, INFO, WARN, ERROR, CRITICAL (default INFO)', default='INFO')
    parser.add_argument('--project-file', help='Path to the *.bpprj file')
    args = parser.parse_args()

    projectFile: Optional[str] = args.project_file
    logLevel: str = args.log_level

    logLevelDict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARN': logging.WARN,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    logging.basicConfig(
        level=logLevelDict[logLevel.upper()],
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
    )

    # TODO: load from settings file
    settings = Settings()
    settingsManager = SettingsManager(settings)

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    widget = MainWindow(settings=settings)
    widget.show()

    widget.signals.closed.connect(lambda: app.quit())
    sys.exit(app.exec())
