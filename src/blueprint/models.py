import logging
from dataclasses import dataclass
from inspect import Signature
from typing import List

from blueprint.settings import Settings, SettingsManager


@dataclass
class Function:
    module: str
    name: str
    signature: Signature


class Project:
    settings: Settings
    functions: List[Function]
    flows: List  # TODO

    logger = logging.getLogger('Project')

    def __init__(self, settings: Settings, functions: List[Function], flows: List):
        self.settings = settings
        self.functions = functions
        self.flows = flows

        self.logger.debug(self.functions)
