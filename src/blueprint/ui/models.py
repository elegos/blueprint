from typing import Optional
from PySide6.QtGui import QFont, QStandardItem
from blueprint.models import Flow, Function


class FnTreeItem(QStandardItem):
    function: Function

    def __init__(self, text: str, function: Optional[Function] = None) -> None:
        super().__init__()

        self.setEditable(False)
        self.setText(text)
        self.setDragEnabled(function is not None)

        self.function = function


class FnPropsPropItem(QStandardItem):
    def __init__(self, text: str, tooltip: Optional[str] = None) -> None:
        super().__init__()

        self.setEditable(False)
        self.setText(text)

        if tooltip:
            self.setToolTip(tooltip)


class FnPropsCategoryItem(FnPropsPropItem):
    def __init__(self, text: str) -> None:
        super().__init__(text=text)

        font = QFont()
        font.setBold(True)

        self.setFont(font)


class FlowListItem(QStandardItem):
    flow: Flow

    def __init__(self, flow: Flow) -> None:
        super().__init__()

        self.flow = flow

        self.setText(self.flow.name)
        self.setEditable(False)
