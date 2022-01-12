import math
import sys
from typing import Union

from PySide6 import QtCore, QtGui
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QTabWidget, QVBoxLayout, QWidget


class MyGraphicsView(QGraphicsView):
    svg_renderer: QSvgRenderer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        svg_data = '''
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <rect width="100%" height="100%" fill="#434343" fill-opacity="1" />
    <g fill-rule="evenodd">
        <g fill="#979797" fill-opacity="1">
            <path opacity=".5" d="M96 95h4v1h-4v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9zm-1 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9z" />
            <path d="M6 5V0H5v5H0v1h5v94h1V6h94V5H6z" />
        </g>
    </g>
</svg>
        '''.encode('utf8')
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

        self.svg_renderer.render(painter, rect)


class WhatsUnderMouse(QtCore.QObject):
    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.MouseButtonPress:
            click_name = watched.objectName().strip() or type(watched)
            print(f'Clicked: {click_name}')

        return super().eventFilter(watched, event)


# if __name__ == '__main__':
#     app = QApplication()
#     app.setObjectName('The application')
#     mouseEventFilter = WhatsUnderMouse()
#     app.installEventFilter(mouseEventFilter)

#     scene = QGraphicsScene()
#     scene.setObjectName('The scene')
#     pen = QtGui.QPen(QtGui.Qt.GlobalColor.yellow)
#     brush = QtGui.QBrush(QtGui.Qt.GlobalColor.red)
#     scene.addRect(10, 10, 100, 100, pen, brush)
#     view = MyGraphicsView(scene)
#     view.setObjectName('The graphics view')

#     view.show()

#     sys.exit(app.exec())

if __name__ == '__main__':
    app = QApplication()
    app.setObjectName('The application')
    mouseEventFilter = WhatsUnderMouse()
    app.installEventFilter(mouseEventFilter)
    main = QWidget()
    main.show()

    layout = QVBoxLayout()
    main.setLayout(layout)
    tabs = QTabWidget(main)
    layout.addWidget(tabs)

    scene = QGraphicsScene()
    scene.setObjectName('The scene')
    pen = QtGui.QPen(QtGui.Qt.GlobalColor.yellow)
    brush = QtGui.QBrush(QtGui.Qt.GlobalColor.red)
    scene.addRect(5, 5, 100, 100, pen, brush)
    view = MyGraphicsView(scene)
    view.setObjectName('The graphics view')

    tabs.addTab(view, 'The view')

    sys.exit(app.exec())
