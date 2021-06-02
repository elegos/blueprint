from dataclasses import dataclass
from inspect import Parameter, Signature
from typing import List


@dataclass
class Function:
    module: str
    name: str
    signature: Signature
