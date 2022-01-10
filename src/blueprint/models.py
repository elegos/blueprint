import logging
import uuid
from dataclasses import dataclass, field
from inspect import Signature
from typing import List

from blueprint.settings import Settings


@dataclass
class Function:
    module: str
    name: str
    signature: Signature


@dataclass
class FlowElement:
    @dataclass
    class ChartCoords:
        x: int
        y: int

    coords: 'FlowElement.ChartCoords'

    function: Function


@dataclass
class Flow:
    name: str
    nodes: List[FlowElement]

    uid: str = field(default_factory=lambda: str(uuid.uuid4()))


class Project:
    settings: Settings
    functions: List[Function]
    flows: List[Flow]

    logger = logging.getLogger('Project')

    def __init__(self, settings: Settings, functions: List[Function], flows: List[Flow]):
        self.settings = settings
        self.functions = functions
        self.flows = flows

        self.logger.debug(self.functions)
