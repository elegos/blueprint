from typing import Any, Optional
from logging import Logger, getLogger

import yaml
from PySide6.QtCore import QObject, Signal, SignalInstance


class SignalChangedAutoTriggered(QObject):
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        signal = getattr(self, f'{name}Changed', None)
        if type(signal) is SignalInstance:
            signal.emit(value)


class DictConvertible:
    def toDict(self, subElement: Any = None) -> dict:
        obj = {}
        objToDict = subElement if subElement else self

        for key, value in objToDict.__dict__.items():
            if isinstance(value, Signal):
                continue

            if callable(getattr(value, 'toDict', None)):
                obj[key] = value
            elif type(value) is list:
                listValues = []
                for val in value:
                    listValues.append(self.toDict(val))
            else:
                obj[key] = value

        return obj


class UI(DictConvertible, SignalChangedAutoTriggered):
    viewFlowsChanged = Signal(bool)
    viewFunctionsChanged = Signal(bool)
    viewObjectPropertiesChanged = Signal(bool)

    viewFlows: bool
    viewFunctions: bool
    viewObjectProperties: bool

    def __init__(
        self, parent: Optional[QObject] = None, viewFlows: bool = True, viewFunctions: bool = True, viewObjectProperties: bool = True
    ) -> None:
        super().__init__(parent=parent)

        self.viewFlows = viewFlows
        self.viewFunctions = viewFunctions
        self.viewObjectProperties = viewObjectProperties


class Settings(QObject, DictConvertible):
    ui: UI

    def __init__(self, ui: Optional[UI] = None, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self.ui = ui if ui else UI()

    @staticmethod
    def fromFile(filePath: str) -> 'Settings':
        with open(filePath, 'rb') as fh:
            return Settings.fromDict(yaml.load(fh))

    @staticmethod
    def fromDict(dictionary: dict) -> 'Settings':
        pass


class SettingsManager(QObject):
    logger: Logger
    settings: Settings

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
