from dataclasses import dataclass
from inspect import Signature


@dataclass
class Function:
    module: str
    name: str
    signature: Signature
