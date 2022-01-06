# This Python file uses the following encoding: utf-8
import inspect
import logging
import os
from io import StringIO
from pathlib import Path
from typing import Callable, Dict

from blueprint.function import Function
from blueprint.project import Project
from blueprint.settings import Settings, SettingsManager
from blueprint.ui.mainwindow.function_models import (FnPropsCategoryItem,
                                                     FnPropsPropItem,
                                                     FnTreeItem)
from blueprint.ui.mainwindow.menu import Menu
from blueprint.ui.qplaintextedit_log_handler import QPlainTextEditLogHandler
from PySide6.QtCore import QEvent, QFile, QObject, Signal
from PySide6.QtGui import QStandardItemModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QFileDialog, QGroupBox,
                               QMainWindow, QPlainTextEdit, QTreeView, QWidget)


class MainWindowSignals(QObject):
    closed = Signal(None)


class MainWindow(QMainWindow):
    signals: MainWindowSignals
    logStream: StringIO

    settings: Settings
    project: Project

    ui: QWidget
    menu: Menu
    flowsGroupBox: QGroupBox
    functionsGroupBox: QGroupBox
    functionsTreeView: QTreeView
    propertiesTreeView: QTreeView
    logViewer: QPlainTextEdit

    def __init__(self, settings: Settings, project: Project = None) -> None:
        super(MainWindow, self).__init__()
        self.signals = MainWindowSignals()
        self.settings = settings
        self.project = project

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
        self.functionsTreeView = self.ui.findChild(
            QTreeView, 'functionsTreeView')
        self.propertiesTreeView = self.ui.findChild(
            QTreeView, 'propertiesTreeView')
        self.logViewer = self.ui.findChild(QPlainTextEdit, 'logViewer')

        self.ui.installEventFilter(self)
        self.setup_functions_tree_view()
        self.setup_function_props_view()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.ui and event.type() == QEvent.Close:
            self.signals.closed.emit()

        return super().eventFilter(watched, event)

    def init_menu(self) -> None:
        self.menu = Menu(ui=self.ui, settings=self.settings)

        self.menu.signals.onExit.connect(
            lambda _: QApplication.instance().quit())

        self.menu.signals.onOpenProjectRoot.connect(
            self.open_project_dialog)

    def init_ui(self) -> None:
        self.flowsGroupBox.setVisible(self.settings.ui.viewFlows)
        self.functionsGroupBox.setVisible(self.settings.ui.viewFunctions)
        self.propertiesTreeView.setVisible(
            self.settings.ui.viewObjectProperties)

    def init_settingsEventHandlers(self) -> None:
        self.settings.ui.viewFlowsChanged.connect(
            lambda visible: self.flowsGroupBox.setVisible(visible))
        self.settings.ui.viewFunctionsChanged.connect(
            lambda visible: self.functionsGroupBox.setVisible(visible))
        self.settings.ui.viewObjectPropertiesChanged.connect(
            lambda visible: self.propertiesTreeView.setVisible(visible))

        self.settings.ui.viewFlowsChanged.connect(self.on_view_hide_event)
        self.settings.ui.viewFunctionsChanged.connect(self.on_view_hide_event)
        self.settings.ui.viewObjectPropertiesChanged.connect(
            self.on_view_hide_event)

    def init_logger(self) -> None:
        logger = logging.getLogger()
        self.logStream = StringIO()
        for handler in logger.handlers:
            logger.removeHandler(handler)

        handler = QPlainTextEditLogHandler(self.logViewer)
        logger.addHandler(handler)

    def on_view_hide_event(self, *args) -> None:
        self.ui.findChild(QWidget, 'leftSideWidget').setVisible(
            self.settings.ui.viewFlows or self.settings.ui.viewFunctions)

        self.ui.findChild(QWidget, 'inspectorWidget').setVisible(
            self.settings.ui.viewObjectProperties)

    def open_project_dialog(self, *args) -> Callable:
        pathStr = QFileDialog.getExistingDirectory(
            self, 'Open project folder...', os.getcwd())

        project_path = Path(pathStr).absolute()

        if not project_path:
            return

        self.settings = Settings(
            filePath=Settings.get_settings_path(project_path), load=True)

        self.project = Project.load(
            SettingsManager.get_instance(self.settings))

        self.load_functions_from_project()

    def setup_functions_tree_view(self):
        view = self.functionsTreeView
        view.setModel(QStandardItemModel())
        view.setHeaderHidden(True)
        view.setDragEnabled(True)

        view.clicked.connect(lambda index: self.load_function_prop(
            index.model().itemFromIndex(index).function))

    def setup_function_props_view(self):
        view = self.propertiesTreeView

        model = QStandardItemModel()
        model.setColumnCount(2)
        model.setHorizontalHeaderLabels(['Category', 'Property', 'Value'])

        view.setModel(model)

    def load_functions_from_project(self):
        model = self.functionsTreeView.model()

        if model.hasChildren():
            model.removeRows(0, model.rowCount())

        if not self.project:
            return

        functions = self.project.functions
        functions.sort(key=lambda fn: f'{fn.module}{fn.name}')

        rootNode = model.invisibleRootItem()
        items: Dict[str, FnTreeItem] = {}
        for fn in functions:
            module_path = fn.module.split('.')
            current_path = ''
            for path in module_path:
                previous_path = current_path
                if not previous_path:
                    current_path = path
                else:
                    current_path = '.'.join([current_path, path])
                if current_path not in items:
                    node = FnTreeItem(text=path)
                    items[current_path] = node
                    if not previous_path:
                        rootNode.appendRow(node)
                    else:
                        items[previous_path].appendRow(node)
            node = FnTreeItem(text=fn.name, function=fn)
            items[fn.module].appendRow(node)

        self.functionsTreeView.collapseAll()

    def load_function_prop(self, fn: Function) -> None:
        model: QStandardItemModel = self.propertiesTreeView.model()

        if model.hasChildren():
            model.removeRows(0, model.rowCount())

        rootItem = model.invisibleRootItem()

        parameters = FnPropsCategoryItem('Params')
        params = fn.signature.parameters
        for param in params:
            param = params[param]
            required = param.default is inspect._empty
            required_tooltip = 'Required' if required else None
            type_str = str(
                param.annotation) if param.annotation is not inspect._empty else ''

            parameters.appendRow([
                FnPropsPropItem(''),
                FnPropsPropItem(('* ' if required else '') +
                                param.name, required_tooltip),
                FnPropsPropItem(type_str, type_str),
            ])

        rootItem.appendRow(parameters)

        if fn.signature.return_annotation is not inspect._empty:
            returns = FnPropsCategoryItem('Return')
            annotation = str(fn.signature.return_annotation)
            returns.appendRow([
                FnPropsPropItem(''),
                FnPropsPropItem('(return value)'),
                FnPropsPropItem(annotation, annotation),
            ])

            rootItem.appendRow(returns)

        self.propertiesTreeView.expandAll()

    def show(self) -> None:
        return self.ui.show()
