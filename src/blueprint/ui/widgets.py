import logging
import math
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from blueprint.models import Function
from PySide6 import QtCore, QtGui
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QFrame, QGraphicsView, QHBoxLayout, QLabel,
                               QSizePolicy, QSpacerItem, QTreeView,
                               QVBoxLayout, QWidget)


class FnTreeView(QTreeView):
    def startDrag(self, supportedActions: QtCore.Qt.DropActions) -> None:
        logging.getLogger(f'{__class__.__name__}::startDrag').debug(
            'TODO QPixmap replace')

        return super().startDrag(supportedActions)


class BlueprintGraphicsView(QGraphicsView):
    svg_renderer: QSvgRenderer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        svg_data = Path(__file__).parent.joinpath(
            'images', 'background', 'graph-paper.svg').read_bytes()
        background_content = QtCore.QByteArray(svg_data)
        self.svg_renderer = QSvgRenderer(background_content)
        self.svg_renderer.setAspectRatioMode(
            QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def drawBackground(self, painter: QtGui.QPainter, rect: Union[QtCore.QRectF, QtCore.QRect]) -> None:
        pattern_size = self.svg_renderer.defaultSize()
        p_width = pattern_size.width()
        p_height = pattern_size.height()

        left_steps = math.ceil(rect.width() / pattern_size.width())
        top_steps = math.ceil(rect.height() / pattern_size.height())

        for w in range(0, left_steps):
            for h in range(0, top_steps):
                left = w * p_width
                top = h * p_height
                for top_multiplier in [1, -1]:
                    for left_multiplier in [1, -1]:
                        rect = QtCore.QRect()
                        rect.setTop(top_multiplier * top)
                        rect.setLeft(left_multiplier * left)
                        rect.setWidth(p_width)
                        rect.setHeight(p_height)

                        self.svg_renderer.render(painter, rect)


class GraphWidget(QWidget):
    header: QFrame
    type: 'GraphWidget.Type'

    _header_label: QLabel
    _subheader_label: QLabel

    central_widget: QFrame

    class Type(Enum):
        FUNCTION = 'f(x)'
        CONSTANT = 'k'
        INPUT = 'x'
        OUTPUT = 'y'
        ENVIRONMENT = 'e'

    def __init__(self, type: 'GraphWidget.Type', parent: Optional[QWidget] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.type = type

    def setup_ui(self) -> None:
        self.setWindowOpacity(0.8)

        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)

        self.header = QFrame(self)
        self.header.setObjectName('header')
        header_layout = QVBoxLayout()
        self.header.setLayout(header_layout)

        png_url = Path(__file__).parent.joinpath(
            'images', 'background', 'spectrum-gradient.png').absolute()
        self.header.setStyleSheet(f'''
            #header {{
                border-image: url("{png_url}") 0 0 0 0 stretch stretch;
            }}
        ''')

        header_size_policy = QSizePolicy()
        header_size_policy.setVerticalPolicy(QSizePolicy.Policy.Maximum)
        header_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Minimum)

        self.header.setSizePolicy(header_size_policy)

        self._header_label = QLabel(self.header)
        self._header_label.setSizePolicy(header_size_policy)
        header_layout.addWidget(self._header_label)

        self._subheader_label = QLabel(self.header)
        self._subheader_label.setStyleSheet('font-style: italic')
        self._subheader_label.setSizePolicy(header_size_policy)
        header_layout.addWidget(self._subheader_label)

        widget_layout.addWidget(self.header)

        self.central_widget = QFrame(self)
        widget_layout.addWidget(self.central_widget)

    def setTitle(self, title: str):
        type_str = self.type.value
        self._header_label.setText(f'<b>{type_str}</b> {title}')

    def setSubtitle(self, subtitle: str):
        self._subheader_label.setText(subtitle)


class FunctionWidget(GraphWidget):
    fn: Function

    def __init__(self, function: Function, parent: Optional[QWidget] = None, *args, **kwargs) -> None:
        super().__init__(GraphWidget.Type.FUNCTION, parent, *args, **kwargs)

        self.fn = function
        self.setup_ui()

    def setup_ui(self) -> None:
        super().setup_ui()

        self.setTitle(self.fn.name)
        self.setSubtitle(self.fn.module)

        layout = QHBoxLayout()
        self.central_widget.setLayout(layout)

        frame_size_policy = QSizePolicy()
        frame_size_policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
        frame_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Maximum)

        inputsFrame = QFrame(self.central_widget)
        inputsFrame.setObjectName('inputs_frame')
        inputsFrame.setSizePolicy(frame_size_policy)
        inputsLayout = QVBoxLayout()
        inputsFrame.setLayout(inputsLayout)
        layout.addWidget(inputsFrame)

        spacer = QSpacerItem(9999, 9999, hData=QSizePolicy.Minimum,
                             vData=QSizePolicy.Minimum)
        layout.addItem(spacer)

        outputsFrame = QFrame(self.central_widget)
        outputsFrame.setObjectName('outputs_frame')
        outputsFrame.setSizePolicy(frame_size_policy)
        outputsLayout = QVBoxLayout()
        outputsFrame.setLayout(outputsLayout)
        layout.addWidget(outputsFrame)

        test_label = QLabel()
        test_label.setText('TEST LEFT')
        inputsLayout.addWidget(test_label)
        inputsFrame.setStyleSheet('''
            #inputs_frame { background-color: blue; }
        ''')

        test_label = QLabel()
        test_label.setText('TEST RIGHT')
        outputsLayout.addWidget(test_label)
        outputsFrame.setStyleSheet('''
            #outputs_frame { background-color: red; }
        ''')
