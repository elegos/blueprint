import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication

from src import Settings, SettingsManager
from src.ui import MainWindow

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log-level', help='DEBUG, INFO, WARN, ERROR, CRITICAL (default INFO)', default='INFO')
    parser.add_argument(
        'project_path', help='Path of a project directory or bpprj file', default=None)
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log_level)

    projectPath: Optional[Path] = None
    if args.project_path:
        projectPath = Path(args.project_path).absolute()

    settingsFilePath = None
    if projectPath:
        basePath = projectPath
        if projectPath.is_file():
            basePath = projectPath.parent.absolute()
        settingsFilePath = Path(os.path.sep.join(
            [str(basePath), '.blueprint', 'settings.yml'])) if projectPath else None
    settings = Settings(filePath=settingsFilePath)
    if settings.filePath:
        settings.load()
    settingsManager = SettingsManager(settings)

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    widget = MainWindow(settings=settings)
    widget.show()

    widget.signals.closed.connect(lambda: app.quit())
    sys.exit(app.exec())
