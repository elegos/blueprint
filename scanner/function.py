import inspect
from dataclasses import dataclass
from datetime import date, datetime
from enum import EnumMeta
from inspect import Parameter, Signature
from json import JSONEncoder
from types import MappingProxyType
from typing import Any

EMPTY_PARAM = '____empty____'


@dataclass
class Function:
    module: str
    name: str
    signature: Signature

    def __str__(self) -> str:
        return f'{self.module}.{self.name}: {self.signature}'

    @staticmethod
    def fromJson(dictionary: dict) -> 'Function':
        sig = dictionary['signature']
        signature = Signature(parameters=[Parameter(
            name=value['name'],
            kind=value['kind'],
            annotation=Parameter.empty if value['annotation'] == EMPTY_PARAM else value['annotation'],
            default=Parameter.empty if value['default'] == EMPTY_PARAM else value['default'],
        ) for value in sig['parameters']], return_annotation=sig['return_annotation'])

        return Function(module=dictionary['module'], name=dictionary['name'], signature=signature)


class FunctionJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Function):
            return obj.__dict__
        elif isinstance(obj, Signature):
            parameters = [{
                'name': param.name,
                'kind': param.kind,
                'annotation': EMPTY_PARAM if param.annotation is Parameter.empty else param.annotation,
                'default': EMPTY_PARAM if param.default is Parameter.empty else param.default,
            } for param in obj.parameters.values()]

            return {
                'parameters': parameters,
                'return_annotation': obj.return_annotation,
            }

        elif isinstance(obj, MappingProxyType):
            return obj.copy()

        elif isinstance(obj, EnumMeta):
            return {e.name: e.value for e in obj}
        
        elif isinstance(obj, datetime):
            return 'datetime.datetime'

        elif isinstance(obj, date):
            return 'datetime.date'
        
        elif isinstance(obj, set):
            return obj

        if '__dict__' in dir(obj):
            return obj.__dict__

        raise Exception(obj.__class__.__name__)

        # return obj.__class__.__name__
