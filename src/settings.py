from dataclasses import dataclass, field
from typing import Any, Optional

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


@dataclass
class Settings(DictConvertible):
    ui: UI = field(default_factory=lambda: UI())

    @staticmethod
    def fromDict() -> 'Settings':
        pass
