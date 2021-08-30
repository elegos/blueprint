import glob
import re
import subprocess
import sys
from importlib import import_module
from inspect import getmembers, isfunction, signature
from os import environ, sep
from pkgutil import iter_modules
from typing import List, Optional, Set

from setuptools import find_packages

from scanner.function import Function


def functionsScanner(
        packagePath: str,
        filter=None) -> List[Function]:
    '''
        Scan the path for all the package's modules functions

        Parameters
        ----------
        packagePath : str
            The base path of the package which has to be scanned
        filter : Literal['regex'] (optional)
            If set, filter out the modules matching the pattern
    '''

    sys.path.append(packagePath)
    pipenvVenv = subprocess.run(
        ['pipenv', '--venv'],
        env={**environ, **{'PIPENV_IGNORE_VIRTUALENVS': '1'}},
        cwd=packagePath,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if pipenvVenv.stdout:
        basePath = pipenvVenv.stdout.strip().decode('utf-8')
        sitePackagesPaths = glob.glob(
            f'{basePath}/**/site-packages', recursive=True)
        for path in sitePackagesPaths:
            sys.path.append(path)

    pattern: Optional[re.Pattern[re.AnyStr @ compile]] = None
    if filter is not None:
        pattern = re.compile(filter)
    modules: Set[str] = set()
    for pkg in find_packages(packagePath):
        if pattern is None or pattern.search(pkg) is None:
            modules.add(pkg)
        for info in iter_modules(
                [f'{packagePath}{sep}{pkg.replace(".", sep)}']):
            if not info.ispkg and (pattern is None
                                   or pattern.search(info.name) is None):
                modules.add(pkg + '.' + info.name)

    result: List[Function] = []
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
