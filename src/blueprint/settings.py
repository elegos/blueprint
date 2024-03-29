import inspect
import os
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, Optional, Type, TypeVar

import yaml

from blueprint.decorators import autoemit

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from PySide6.QtCore import QObject, Signal, SignalInstance

BLUEPRINT_FOLDER_NAME = '.blueprint'
T = TypeVar('T')


class DictConvertible:
    @staticmethod
    def scalarValue(value) -> Any:
        if type(value) in [str, int, float, bool] or value is None:
            return value

        return str(value)

    def fromDict(self: Type[T], dictionary: dict) -> T:
        for member in inspect.getmembers(self):
            name, _ = member
            if name in dictionary:
                setattr(self, name, dictionary[name])

    def toDict(self, subElement: Any = None) -> dict:
        obj = {}
        objToDict = subElement if subElement else self

        for key, value in objToDict.__dict__.items():
            if isinstance(value, Signal) or key in ['filePath', 'logger']:
                continue

            if callable(getattr(value, 'toDict', None)):
                obj[key] = value.toDict()
            elif type(value) is list:
                listValues = []
                for val in value:
                    listValues.append(self.toDict(val))
            else:
                obj[key] = DictConvertible.scalarValue(value)

        return obj


class UI(QObject, DictConvertible):
    viewFlowsChanged = Signal(bool)
    viewFunctionsChanged = Signal(bool)
    viewObjectPropertiesChanged = Signal(bool)

    viewFlows = autoemit('viewFlows', 'viewFlowsChanged', bool)
    viewFunctions = autoemit('viewFunctions', 'viewFunctionsChanged', bool)
    viewObjectProperties = autoemit(
        'viewObjectProperties', 'viewObjectPropertiesChanged', bool)

    def __init__(
        self, parent: Optional[QObject] = None, viewFlows: bool = True, viewFunctions: bool = True, viewObjectProperties: bool = True
    ) -> None:
        super().__init__(parent=parent)

        self.viewFlows = viewFlows
        self.viewFunctions = viewFunctions
        self.viewObjectProperties = viewObjectProperties


class Settings(QObject, DictConvertible):
    filePath: Optional[Path]
    logger: Logger
    ui: UI

    def __init__(
        self, filePath: Path = None, ui: Optional[UI] = None,
        parent: Optional[QObject] = None, load: bool = False
    ) -> None:
        super().__init__(parent=parent)
        self.ui = ui if ui else UI()
        self.filePath = filePath.absolute() if filePath else None
        self.logger = getLogger('Settings')

        if load and self.filePath:
            self.load()

    @staticmethod
    def get_settings_path(project_path: Path) -> Path:
        return project_path.joinpath(BLUEPRINT_FOLDER_NAME, 'settings.yml')

    def setFilePath(self, path: str) -> None:
        self.filePath = Path(path).absolute()

    def load(self):
        if not self.filePath or not self.filePath.exists():
            self.logger.warn(
                'Trying to load settings without a settings file, aborting.')
            return

        with self.filePath.open('r') as fh:
            dictionary = yaml.load(fh, Loader=Loader)
            self.ui.fromDict(dictionary['ui'])

    def get_project_root(self) -> Optional[Path]:
        if self.filePath:
            return self.filePath.parent.parent

        return None


class SettingsManager(QObject):
    logger: Logger
    settings: Settings

    __instances = {}

    @staticmethod
    def get_instance(settings: Settings, parent: Optional[QObject] = None) -> Optional['SettingsManager']:
        if not settings.filePath:
            return None

        if str(settings.filePath) in SettingsManager.__instances:
            return SettingsManager.__instances[str(settings.filePath)]

        manager = SettingsManager(settings, parent=parent)
        SettingsManager.__instances[str(settings.filePath)] = manager

        return manager

    def __init__(self, settings: Settings, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.logger = getLogger('SettingsManager')

        self.settings = settings
        self.installUpdatesWatcher()

    def installUpdatesWatcher(self, obj: Optional[QObject] = None):
        obj = obj if obj else self.settings

        for attr in obj.__dict__.values():
            if type(attr) is SignalInstance:
                attr.connect(self.updateWatcher)
            elif isinstance(attr, QObject):
                self.installUpdatesWatcher(attr)

    def updateWatcher(self, *_) -> None:
        self.logger.debug('Detected settings change')
        if not self.settings.filePath:
            return
        bpDir = self.settings.filePath.parent
        if not bpDir.exists():
            os.mkdir(bpDir)

        with open(self.settings.filePath, 'w') as fh:
            yaml.dump(self.settings.toDict(), stream=fh, Dumper=Dumper)
