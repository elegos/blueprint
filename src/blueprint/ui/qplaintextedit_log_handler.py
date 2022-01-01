import logging

from PySide6.QtWidgets import QPlainTextEdit


class QPlainTextEditLogHandler(logging.Handler):
    widget: QPlainTextEdit

    def __init__(self, widget: QPlainTextEdit) -> None:
        super().__init__(level=logging.root.level)

        self.setFormatter(logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s'))

        self.widget = widget
        self.widget.setReadOnly(True)
        self.widget.setCenterOnScroll(True)

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self.widget.appendPlainText(message)
        self.widget.ensureCursorVisible()
