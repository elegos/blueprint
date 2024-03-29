# This Python file uses the following encoding: utf-8
import inspect
import logging
import os
from io import StringIO
from pathlib import Path
from threading import Thread
from typing import Callable, Dict

from blueprint.model_functions import load_project
from blueprint.models import Flow, Function, Project
from blueprint.settings import Settings
from blueprint.ui.mainwindow.menu import Menu
from blueprint.ui.models import (FlowListItem, FnPropsCategoryItem,
                                 FnPropsPropItem, FnTreeItem)
from blueprint.ui.qplaintextedit_log_handler import QPlainTextEditLogHandler
from blueprint.ui.widgets import (BlueprintGraphicsView, FnTreeView,
                                  FunctionGraphicWidget)
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QEvent, QFile, QObject, QTimer, Signal
from PySide6.QtGui import QStandardItemModel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QFileDialog, QGraphicsScene,
                               QGroupBox, QInputDialog, QLineEdit, QListView,
                               QMainWindow, QMessageBox, QPlainTextEdit,
                               QPushButton, QStatusBar, QTabWidget, QTreeView,
                               QWidget)


class MainWindowSignals(QObject):
    closed = Signal(None)


class MainWindow(QMainWindow):
    signals: MainWindowSignals
    logStream: StringIO

    settings: Settings
    project: Project
    graphics_views: Dict[str, BlueprintGraphicsView]

    ui: QWidget
    menu: Menu
    flowsGroupBox: QGroupBox

    functionsGroupBox: QGroupBox
    functionsTreeView: FnTreeView
    functionsFilterLineEdit: QLineEdit
    functionsFilter: str

    flowsListView: QListView
    newFlowPushButton: QPushButton
    deleteFlowPushButton: QPushButton

    blueprintsTabWidget: QTabWidget

    status_bar: QStatusBar

    propertiesTreeView: QTreeView
    logViewer: QPlainTextEdit

    def __init__(self, settings: Settings, project: Project = None) -> None:
        super(MainWindow, self).__init__()
        self.signals = MainWindowSignals()
        self.settings = settings
        self.project = project
        self.graphics_views = {}

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

        # Can't load a custom component from .ui files.
        # Replace the placeholder with the real widget.
        fnViewPlaceholder: QTreeView = self.ui.findChild(
            QTreeView, 'functionsTreeView')
        fnTreeViewParent: QWidget = fnViewPlaceholder.parent()
        self.functionsTreeView = FnTreeView(parent=fnTreeViewParent)
        fnTreeViewParent.layout().replaceWidget(
            fnViewPlaceholder, self.functionsTreeView)
        fnViewPlaceholder.deleteLater()

        self.functionsFilterLineEdit = self.ui.findChild(
            QLineEdit, 'functionsFilterLineEdit')
        self.functionsFilter = ''

        self.propertiesTreeView = self.ui.findChild(
            QTreeView, 'propertiesTreeView')
        self.logViewer = self.ui.findChild(QPlainTextEdit, 'logViewer')

        self.flowsListView = self.ui.findChild(
            QListView, 'flowsListView')
        self.newFlowPushButton = self.ui.findChild(
            QPushButton, 'newFlowPushButton')
        self.deleteFlowPushButton = self.ui.findChild(
            QPushButton, 'deleteFlowPushButton')

        self.blueprintsTabWidget = self.ui.findChild(
            QTabWidget, 'blueprintsTabWidget'
        )

        self.status_bar = self.ui.findChild(QStatusBar, 'statusbar')

        self.ui.installEventFilter(self)
        self.setup_flows_management_ui()
        self.setup_flows_tab_group()
        self.setup_functions_tree_view()
        self.setup_functions_filter()
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

        logging.getLogger('UI').debug('Logger initialized')

    def on_view_hide_event(self, *args) -> None:
        self.ui.findChild(QWidget, 'leftSideWidget').setVisible(
            self.settings.ui.viewFlows or self.settings.ui.viewFunctions)

        self.ui.findChild(QWidget, 'inspectorWidget').setVisible(
            self.settings.ui.viewObjectProperties)

    def on_functions_filter_edit(self, *args) -> None:
        self.functionsFilter = self.functionsFilterLineEdit.text()
        self.load_functions_from_project()

    def load_project(self):
        self.status_bar.showMessage('Loading project...')
        self.project = load_project(self.settings)

        self.status_bar.showMessage('Project loaded', 5000)
        self.load_functions_from_project()
        self.load_flows_from_project()

    def open_project_dialog(self, *args) -> Callable:
        pathStr = QFileDialog.getExistingDirectory(
            self, 'Open project folder...', os.getcwd())

        project_path = Path(pathStr).absolute()

        if not project_path:
            return

        self.settings = Settings(
            filePath=Settings.get_settings_path(project_path), load=True)

        self.project_load_thread = Thread(
            target=self.load_project)
        self.project_load_thread.start()

    def on_new_flow(self, *args):
        logger = logging.getLogger('on_new_flow')

        dialog = QInputDialog(self)
        name = ''
        name, ok = dialog.getText(self, 'Add new flow', 'Flow name:')
        existing_flow = next(
            (flow for flow in self.project.flows if flow.name == name), None)

        if ok:
            if name and not existing_flow:
                flow = Flow(name=name, nodes=[])
                self.project.flows.append(flow)
                self.project.flows.sort(key=lambda flow: flow.name)

                self.load_flows_from_project()

            if not name or existing_flow:
                error_dialog = QMessageBox(dialog)
                error_dialog.setWindowTitle('New flow error')
                error_dialog.setWindowModality(
                    QtCore.Qt.WindowModality.ApplicationModal)
                error_dialog.setText(
                    'A flow must have a unique, non-empty name.')

                def on_close():
                    error_dialog.close()
                    self.on_new_flow()

                error_dialog.buttonClicked.connect(on_close)

                error_dialog.show()

    def on_flow_delete(self, *args):
        logger = logging.getLogger('on_flow_delete')

        logger.debug('TODO')

    def on_flow_open(self, index: QtCore.QModelIndex):
        flow_name = index.data()
        flow = next(
            flow for flow in self.project.flows if flow.name == flow_name)

        flow_scene = QGraphicsScene(self)

        if flow.uid in self.graphics_views:
            previous_tab = self.graphics_views[flow.uid]
            previous_tab.deleteLater()

        self.graphics_views[flow.uid] = BlueprintGraphicsView(flow, flow_scene)
        view = self.graphics_views[flow.uid]
        view.setObjectName(f'{flow.uid}_scene')

        self.blueprintsTabWidget.addTab(
            view, flow_name)

        self.blueprintsTabWidget.setCurrentIndex(
            self.blueprintsTabWidget.indexOf(view))

    def on_flow_close(self, tab_index: int):
        widget: BlueprintGraphicsView = self.blueprintsTabWidget.widget(
            tab_index)

        if widget.flow.uid in self.graphics_views:
            self.graphics_views.pop(widget.flow.uid)
        self.blueprintsTabWidget.removeTab(tab_index)

    def on_flow_item_change(self, tab_index: int):
        if not self.project:
            return

        edit_name_dialog = QInputDialog(self)
        text, ok = edit_name_dialog.getText(
            self, "Flow's new name", 'Choose a new name')
        if text and ok:
            self.on_flow_item_changed(tab_index, text)

    def on_flow_item_changed(self, tab_index: int, new_name: str):
        logger = logging.getLogger('on_flow_item_changed')

        current_name = self.blueprintsTabWidget.tabText(tab_index)
        existing_flow = next(
            (flow for flow in self.project.flows if flow.name == current_name), None)

        if not existing_flow or new_name == existing_flow.name:
            return

        other_existing_flow = next(
            (flow for flow in self.project.flows if flow.name ==
             new_name and flow != existing_flow),
            None
        )

        if not new_name or other_existing_flow:
            self.status_bar.showMessage(
                'Flow name must be non-empty and unique.', 5000)

            return

        existing_flow.name = new_name
        self.blueprintsTabWidget.setTabText(tab_index, new_name)

        self.load_flows_from_project()

    def setup_flows_management_ui(self):
        self.newFlowPushButton.clicked.connect(self.on_new_flow)
        self.deleteFlowPushButton.clicked.connect(self.on_flow_delete)

        list_model = QStandardItemModel()
        self.flowsListView.setModel(list_model)
        self.flowsListView.doubleClicked.connect(self.on_flow_open)

        if not self.project:
            self.newFlowPushButton.setEnabled(False)
            self.deleteFlowPushButton.setEnabled(False)

        self.load_flows_from_project()

    def setup_flows_tab_group(self):
        self.blueprintsTabWidget.tabBarDoubleClicked.connect(
            self.on_flow_item_change)

        self.blueprintsTabWidget.setTabsClosable(True)
        tabBar = self.blueprintsTabWidget.tabBar()
        tabBar.tabCloseRequested.connect(self.on_flow_close)

        # DEMO
        fn = Function('module.name', 'name', None)

        self.blueprintsTabWidget.addTab(
            FunctionGraphicWidget(fn), 'FunctionWidget demo')

    def setup_functions_tree_view(self):
        view = self.functionsTreeView
        view.setModel(QStandardItemModel())
        view.setHeaderHidden(True)
        view.setDragEnabled(True)

        view.clicked.connect(lambda index: self.load_function_prop(
            index.model().itemFromIndex(index).function))

    def setup_functions_filter(self):
        functions_timer = QTimer(self)
        functions_timer.setSingleShot(True)
        functions_timer.setInterval(300)
        functions_timer.timeout.connect(self.on_functions_filter_edit)

        self.functionsFilterLineEdit.textChanged.connect(
            lambda: functions_timer.start())

    def setup_function_props_view(self):
        view = self.propertiesTreeView

        model = QStandardItemModel()
        model.setColumnCount(2)
        model.setHorizontalHeaderLabels(['Category', 'Property', 'Value'])

        view.setModel(model)

    def load_flows_from_project(self):
        logger = logging.getLogger('load_flows_from_project')

        model: QStandardItemModel = self.flowsListView.model()
        if model.hasChildren():
            model.removeRows(0, model.rowCount())

        if not self.project:
            self.newFlowPushButton.setEnabled(False)
            self.deleteFlowPushButton.setEnabled(False)

            return

        rootNode = model.invisibleRootItem()
        for flow in self.project.flows:
            rootNode.appendRow(FlowListItem(flow))

        self.newFlowPushButton.setEnabled(True)
        self.deleteFlowPushButton.setEnabled(True)

    def load_functions_from_project(self):
        model = self.functionsTreeView.model()

        if model.hasChildren():
            model.removeRows(0, model.rowCount())

        if not self.project:
            return

        functions = self.project.functions
        if self.functionsFilter:
            functions = list(filter(
                lambda fn: self.functionsFilter in f'{fn.module}.{fn.name}', functions))
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
        if not fn:
            return

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
