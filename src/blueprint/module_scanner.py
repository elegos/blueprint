import logging
from pathlib import Path
import re
import sys
from importlib import import_module
from inspect import getmembers, isfunction, signature
from os import sep
from pkgutil import iter_modules
from typing import List, Literal, Optional, Set, Union

from setuptools import find_packages

from blueprint.function import Function


def functions_scanner(
        packagePath: Union[Path, str],
        filter: Optional[Literal['regex']] = None) -> List[Function]:
    '''
        Scan the path for all the package's modules functions

        Parameters
        ----------
        packagePath : str
            The base path of the package which has to be scanned
        filter : Literal['regex'] (optional)
            If set, filter out the modules matching the pattern
    '''

    pattern: Optional[re.Pattern[re.AnyStr @ compile]] = None
    if filter is not None:
        pattern = re.compile(filter)
    modules: Set[str] = set()

    result: List[Function] = []
    try:
        for pkg in find_packages(str(packagePath)):
            if pattern is None or pattern.search(pkg) is None:
                modules.add(pkg)
            for info in iter_modules(
                    [f'{packagePath}{sep}{pkg.replace(".", sep)}']):
                if not info.ispkg and (pattern is None
                                       or pattern.search(info.name) is None):
                    modules.add(pkg + '.' + info.name)

        for module in modules:
            moduleObj = import_module(module)
            moduleFunctions = [
                member for member in getmembers(moduleObj, isfunction)
                if member[1].__module__ == moduleObj.__name__
            ]

            for fn in moduleFunctions:
                result.append(
                    Function(module=module, name=fn[0],
                             signature=signature(fn[1])))

        return result
    except ModuleNotFoundError as ex:
        logging.getLogger('module_scanner').error(
            f'{ex.msg}\n'
            + '\nYou are either missing it in your system,'
            + ' or you are using the scanner outside its virtual environment.\n'
        )
