import json
import logging
import os
from posixpath import abspath
import subprocess
from scanner.function import Function
from typing import List
from PySide6.QtCore import QObject

from src.singleton import Singleton


class ProjectSettings(QObject, Singleton):
    pass


class ProjectFunctions(QObject, Singleton):
    logger: logging.Logger
    functions: List[Function]

    def __init__(self):
        self.logger = logging.getLogger('Project functions')

    def loadFunctions(self, path: str) -> None:
        rootDir = abspath(os.path.dirname(
            os.path.realpath(__file__)) + os.path.sep + '..')
        self.logger.info(f'Scanning package folder: {path}')

        scanResult = subprocess.run(
            ['python', f'{rootDir}{os.path.sep}scanner.py',
                '--package-path', path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # TODO: handle non-empty scanResult.stderr
        rawData = json.loads(scanResult.stdout)
        self.functions = [Function.fromJson(datum) for datum in rawData]
        self.logger.info(f'Scanning process finish')

        # TODO send scan finish signal
