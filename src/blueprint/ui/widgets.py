import pickle
from enum import Enum
from pathlib import Path
from typing import Optional

from blueprint.models import Function
from blueprint.ui.models import FnTreeItem
from PySide6 import QtCore, QtGui
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QFrame, QGraphicsView, QHBoxLayout, QLabel,
                               QSizePolicy, QSpacerItem, QTreeView,
                               QVBoxLayout, QWidget)


class FnTreeView(QTreeView):
    def startDrag(self, supportedActions: QtCore.Qt.DropActions) -> None:
        index = self.currentIndex()
        model: QtGui.QStandardItemModel = self.model()
        fn_item: FnTreeItem = model.itemFromIndex(index)

        if type(fn_item) != FnTreeItem:
            return super().startDrag(supportedActions)

        widget = FunctionGraphicWidget(fn_item.function)

        # QPixmap preparation
        pixmap = widget.grab(QtCore.QRect(
            QtCore.QPoint(0, 0), QtCore.QSize(-1, -1)))
        # the default pixmap is completely opaque, so it will be painted semi-transparently
        pm_image = QtGui.QImage(pixmap.size(), QtGui.QImage.Format_ARGB32)
        pm_painter = QtGui.QPainter(pm_image)
        pm_painter.setOpacity(0.45)
        pm_painter.drawPixmap(QtCore.QPoint(0, 0), pixmap)
        pm_painter.end()
        pixmap = QtGui.QPixmap.fromImage(pm_image)

        mime_data = QtCore.QMimeData()
        mime_data.setData('binary/pickle', pickle.dumps(fn_item.function))

        drag = QtGui.QDrag(self)
        drag.setPixmap(pixmap)
        drag.setMimeData(mime_data)
        drag.exec(QtCore.Qt.CopyAction)


class BlueprintGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        svg_data = Path(__file__).parent.joinpath(
            'images', 'background', 'graph-paper.svg').read_bytes()
        background_content = QtCore.QByteArray(svg_data)
        svg_renderer = QSvgRenderer(background_content)
        svg_renderer.setAspectRatioMode(
            QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        brush_pixmap = QtGui.QPixmap(svg_renderer.defaultSize())

        brush_painter = QtGui.QPainter(brush_pixmap)
        svg_renderer.render(brush_painter, brush_pixmap.rect())
        brush_painter.end()

        self.setBackgroundBrush(QtGui.QBrush(brush_pixmap))


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
        widget_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(widget_layout)
        self.setContentsMargins(0, 0, 0, 0)

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


class FunctionGraphicWidget(GraphWidget):
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
        layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(layout)

        frame_size_policy = QSizePolicy()
        frame_size_policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
        frame_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Maximum)

        inputs_frame = QFrame(self.central_widget)
        inputs_frame.setObjectName('inputs_frame')
        inputs_frame.setSizePolicy(frame_size_policy)
        inputs_frame.setContentsMargins(0, 0, 0, 0)
        inputs_layout = QVBoxLayout()
        inputs_frame.setLayout(inputs_layout)
        layout.addWidget(inputs_frame)

        spacer = QSpacerItem(0, 0, hData=QSizePolicy.Expanding,
                             vData=QSizePolicy.Expanding)
        layout.addItem(spacer)

        outputs_frame = QFrame(self.central_widget)
        outputs_frame.setObjectName('outputs_frame')
        outputs_frame.setSizePolicy(frame_size_policy)
        outputs_layout = QVBoxLayout()
        outputs_frame.setLayout(outputs_layout)
        layout.addWidget(outputs_frame)

        test_label = QLabel()
        test_label.setText('TEST LEFT')
        inputs_layout.addWidget(test_label)
        inputs_frame.setStyleSheet('''
            #inputs_frame { background-color: blue; }
        ''')

        test_label = QLabel()
        test_label.setText('TEST RIGHT')
        outputs_layout.addWidget(test_label)
        outputs_frame.setStyleSheet('''
            #outputs_frame { background-color: red; }
        ''')
