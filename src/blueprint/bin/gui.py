import argparse
import logging
import sys
from pathlib import Path
from typing import Optional
from PySide6 import QtCore
from PySide6.QtGui import QIcon

from PySide6.QtWidgets import QApplication
from blueprint.model_functions import load_project

from blueprint.settings import Settings
from blueprint.ui.mainwindow.mainwindow import MainWindow


class WhatsUnderMouse(QtCore.QObject):
    logger: logging.Logger

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(__class__.__name__)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.MouseButtonPress:
            click_name = watched.objectName().strip() or type(watched)
            self.logger.debug(click_name)

        return super().eventFilter(watched, event)


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
    project = None
    if settings.get_project_root():
        project = load_project(settings)

    app = QApplication([])
    if args.log_level.lower() == 'debug':
        mouseEventFilter = WhatsUnderMouse()
        app.installEventFilter(mouseEventFilter)
    icon = QIcon()
    icon.addFile(str(Path(__file__).parent.parent.joinpath(
        'ui', 'images', 'icons', 'blueprint-icon.svg')))
    app.setWindowIcon(icon)
    app.setQuitOnLastWindowClosed(False)
    widget = MainWindow(settings=settings, project=project)
    widget.load_functions_from_project()
    widget.show()

    widget.signals.closed.connect(lambda: app.quit())
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
