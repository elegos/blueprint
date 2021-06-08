# This Python file uses the following encoding: utf-8
from io import StringIO
import logging
import os
from pathlib import Path
from src.ui.qplaintextedit_log_handler import QPlainTextEditLogHandler
from src.settings import Settings

from PySide6.QtWidgets import QApplication, QFileDialog, QGroupBox, QMainWindow, QPlainTextEdit, QTableWidget, QWidget
from PySide6.QtCore import QDir, QEvent, QFile, QObject, Signal
from PySide6.QtUiTools import QUiLoader
from src.ui.mainwindow.menu import Menu


class MainWindowSignals(QObject):
    closed = Signal(None)


class MainWindow(QMainWindow):
    signals: MainWindowSignals
    logStream: StringIO

    settings: Settings
    ui: QWidget
    menu: Menu
    flowsGroupBox: QGroupBox
    functionsGroupBox: QGroupBox
    propertiesTableWidget: QTableWidget
    logViewer: QPlainTextEdit

    def __init__(self, settings: Settings) -> None:
        super(MainWindow, self).__init__()
        self.signals = MainWindowSignals()
        self.settings = settings

        self.load_ui()
        self.init_ui()
        self.init_menu()
        self.init_settingsEventHandlers()

        self.init_logger()

    def load_ui(self) -> None:
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / 'form.ui')
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.flowsGroupBox = self.ui.findChild(QGroupBox, 'flowsGroupBox')
        self.functionsGroupBox = self.ui.findChild(
            QGroupBox, 'functionsGroupBox')
        self.propertiesTableWidget = self.ui.findChild(
            QTableWidget, 'propertiesTableWidget')
        self.logViewer = self.ui.findChild(QPlainTextEdit, 'logViewer')

        self.ui.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.ui and event.type() == QEvent.Close:
            self.signals.closed.emit()

        return super().eventFilter(watched, event)

    def init_menu(self) -> None:
        self.menu = Menu(ui=self.ui, settings=self.settings)

        self.menu.signals.onExit.connect(
            lambda _: QApplication.instance().quit())

        self.menu.signals.onOpenProject.connect(self.openProjectDialog)

    def init_ui(self) -> None:
        self.flowsGroupBox.setVisible(self.settings.ui.viewFlows)
        self.functionsGroupBox.setVisible(self.settings.ui.viewFunctions)
        self.propertiesTableWidget.setVisible(
            self.settings.ui.viewObjectProperties)

    def init_settingsEventHandlers(self) -> None:
        self.settings.ui.viewFlowsChanged.connect(
            lambda visible: self.flowsGroupBox.setVisible(visible))
        self.settings.ui.viewFunctionsChanged.connect(
            lambda visible: self.functionsGroupBox.setVisible(visible))
        self.settings.ui.viewObjectPropertiesChanged.connect(
            lambda visible: self.propertiesTableWidget.setVisible(visible))

        self.settings.ui.viewFlowsChanged.connect(self.onViewHideEvent)
        self.settings.ui.viewFunctionsChanged.connect(self.onViewHideEvent)
        self.settings.ui.viewObjectPropertiesChanged.connect(
            self.onViewHideEvent)

    def init_logger(self) -> None:
        logger = logging.getLogger()
        self.logStream = StringIO()
        for handler in logger.handlers:
            logger.removeHandler(handler)

        handler = QPlainTextEditLogHandler(self.logViewer)
        logger.addHandler(handler)

    def onViewHideEvent(self, *args) -> None:
        self.ui.findChild(QWidget, 'leftSideWidget').setVisible(
            self.settings.ui.viewFlows or self.settings.ui.viewFunctions)

        self.ui.findChild(QWidget, 'inspectorWidget').setVisible(
            self.settings.ui.viewObjectProperties)

    def openProjectDialog(self, _) -> None:
        projectFile, _ = QFileDialog.getOpenFileName(
            self, 'Open project file...', QDir.homePath(), 'Project file (*.bpprj)')

        print(projectFile)

    def show(self) -> None:
        return self.ui.show()
