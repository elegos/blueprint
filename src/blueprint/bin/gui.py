import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from blueprint.project import Project

from blueprint.settings import Settings, SettingsManager
from blueprint.ui.mainwindow.mainwindow import MainWindow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log-level', help='DEBUG, INFO, WARN, ERROR, CRITICAL (default INFO)', default='INFO')
    parser.add_argument(
        '--project-path', help='Path of the project directory', default=None)
    args = parser.parse_args()

    logLevel: str = args.log_level
    logging.getLogger().setLevel(logging.getLevelName(logLevel))

    projectPath: Optional[Path] = None
    if args.project_path:
        projectPath = Path(args.project_path).absolute()

    settingsFilePath = None
    if projectPath:
        basePath = projectPath
        settingsFilePath = Settings.get_settings_path(
            basePath) if projectPath else None

    settings = Settings(filePath=settingsFilePath, load=True)
    if settings.get_project_root():
        project = Project.load(SettingsManager.get_instance(settings))

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    widget = MainWindow(settings=settings)
    widget.show()

    widget.signals.closed.connect(lambda: app.quit())
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
