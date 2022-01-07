import logging
from PySide6.QtCore import QObject, Signal, SignalInstance

from PySide6.QtWidgets import QPlainTextEdit


class LogObject(QObject):
    signal: SignalInstance = Signal(str)


class QPlainTextEditLogHandler(logging.Handler):
    widget: QPlainTextEdit
    log_object: LogObject

    def __init__(self, widget: QPlainTextEdit) -> None:
        super().__init__(level=logging.root.level)

        self.setFormatter(logging.Formatter(
            '%(asctime)s [%(name)s] %(levelname)s: %(message)s'))

        self.widget = widget
        self.widget.setReadOnly(True)
        self.widget.setCenterOnScroll(True)

        self.log_object = LogObject()
        self.log_object.signal.connect(self.on_message_emitted)

    def on_message_emitted(self, message: str) -> None:
        self.widget.appendPlainText(message)
        self.widget.ensureCursorVisible()

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self.log_object.signal.emit(message)
