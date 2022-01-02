from blueprint.settings import Settings
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget


class MenuSignals(QObject):
    # File
    onOpenProjectRoot = Signal(bool)
    onExit = Signal(bool)
    # Project
    onProjectSettings = Signal(bool)
    onNewFlow = Signal(bool)
    onManageFlows = Signal(bool)
    # View
    onViewFlows = Signal(bool)
    onViewFunctions = Signal(bool)
    onViewObjectProperties = Signal(bool)


class Menu:
    signals: MenuSignals
    settings: Settings

    # File
    actionOpenProjectRoot: QAction
    actionExit: QAction
    # Project
    actionProjectSettings: QAction
    actionNewFlow: QAction
    actionManageFlows: QAction
    # View
    actionViewFlows: QAction
    actionViewFunctions: QAction
    actionViewObjectProperties: QAction

    def bindActions(self) -> None:
        self.signals = MenuSignals()
        self.actionOpenProjectRoot.triggered.connect(
            self.signals.onOpenProjectRoot)
        self.actionProjectSettings.triggered.connect(
            self.signals.onProjectSettings)
        self.actionNewFlow.triggered.connect(self.signals.onNewFlow)
        self.actionManageFlows.triggered.connect(self.signals.onManageFlows)
        self.actionExit.triggered.connect(self.signals.onExit)

        self.actionViewFlows.triggered.connect(
            lambda val: setattr(self.settings.ui, 'viewFlows', val))
        self.actionViewFunctions.triggered.connect(
            lambda val: setattr(self.settings.ui, 'viewFunctions', val))
        self.actionViewObjectProperties.triggered.connect(
            lambda val: setattr(self.settings.ui, 'viewObjectProperties', val))

    def setupActionStates(self) -> None:
        self.actionViewFlows.setChecked(self.settings.ui.viewFlows)
        self.actionViewFunctions.setChecked(self.settings.ui.viewFunctions)
        self.actionViewObjectProperties.setChecked(
            self.settings.ui.viewObjectProperties)

    def __init__(self, ui: QWidget, settings: Settings) -> None:
        self.settings = settings

        self.actionOpenProjectRoot = ui.findChild(
            QAction, 'actionOpen_project_root')
        self.actionProjectSettings = ui.findChild(
            QAction, 'actionProject_settings')
        self.actionExit = ui.findChild(QAction, 'actionExit')

        self.actionNewFlow = ui.findChild(QAction, 'actionNew_flow')
        self.actionManageFlows = ui.findChild(QAction, 'actionManage_flows')

        self.actionViewFlows = ui.findChild(QAction, 'actionViewFlows')
        self.actionViewFunctions = ui.findChild(QAction, 'actionViewFunctions')
        self.actionViewObjectProperties = ui.findChild(
            QAction, 'actionViewObjectProperties')

        self.bindActions()
        self.setupActionStates()
