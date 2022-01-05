from typing import Optional
from PySide6.QtGui import QStandardItem
from blueprint.function import Function


class TreeItem(QStandardItem):
    function: Function

    def __init__(self, text: str, function: Optional[Function] = None):
        super().__init__()

        self.setEditable(False)
        self.setText(text)
        self.setDragEnabled(function is not None)

        self.function = function
