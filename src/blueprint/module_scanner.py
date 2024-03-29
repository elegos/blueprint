import logging
import sys
from configparser import ConfigParser
from importlib import import_module
from inspect import getmembers, isfunction, signature
from os import sep
from pathlib import Path
from pkgutil import iter_modules
from typing import List, Optional, Pattern, Union

from setuptools import find_packages

from blueprint.models import Function


def get_package_modules(package_name: Path, pattern: Optional[Pattern]) -> List[str]:
    result = [package_name]

    try:
        module = import_module(package_name)
        package_path = Path(module.__file__).parent

        for module_info in iter_modules([str(package_path)]):
            module_import = f'{package_name}.{module_info.name}'

            if module_info.ispkg:
                result.extend(get_package_modules(module_import, pattern))
            elif not pattern or not pattern.search(module_info.name):
                result.append(module_import)
    except ImportError as err:
        pass

    return result


def get_top_level_packages(distribution_name: str) -> List[str]:
    top_level = []
    if sys.version_info[0] == 3 and sys.version_info[1] < 8:
        from pkg_resources import get_distribution

        dist = get_distribution(distribution_name)
        if not dist.has_metadata('top_level.txt'):
            logging.getLogger(__name__).warning(
                "Unable to locate distribution's top_level.txt")

            return top_level
        top_level = list(filter(lambda x: not not x,
                                dist.get_metadata('top_level.txt').split('\n')))
    else:
        # Python 3.8+
        from importlib import metadata
        init_files = [(len(str(path).split('/')), path) for path in metadata.distribution(
            distribution_name).files if str(path).endswith('__init__.py')]

        if init_files:
            min_path = min(init_files, key=lambda x: x[0])[0]
            top_level = ['.'.join(str(ppath[1]).split('/')[:-1])
                         for ppath in init_files if ppath[0] == min_path]

    logging.getLogger(__name__).debug(top_level)

    return top_level


def functions_scanner(
        src_root: Union[Path, str],
        filter: str = None) -> List[Function]:
    '''
        Scan the path for all the package's modules functions

        Parameters
        ----------
        packagePath : str
            The base path of the package which has to be scanned
        filter : str (optional)
            If set, filter out the modules matching the regex pattern
    '''

    pattern: Optional[Pattern] = None
    if filter is not None:
        pattern = compile(filter)
    modules: List[str] = []

    pipfilePath = src_root.joinpath('Pipfile')
    requirementsPath = src_root.joinpath('requirements.txt')
    if pipfilePath.exists():
        parser = ConfigParser()
        parser.read(pipfilePath)
        if parser.has_section('packages'):
            for distribution_name in parser['packages'].keys():
                top_level_packages = get_top_level_packages(distribution_name)

                for top_level in top_level_packages:
                    modules.extend(get_package_modules(top_level, pattern))

    elif requirementsPath.exists():
        moduleNameRe = compile(r'^([^~=<>]+)')
        with requirementsPath.open('r') as fh, fh.readlines() as lines:
            lines: List[str] = lines
            for line in lines:
                matches = moduleNameRe.match(line.strip())
                if not matches:
                    continue
                distribution_name = matches[1]
                modules.append(get_package_modules(distribution_name))

    result: List[Function] = []
    try:
        for pkg in find_packages(str(src_root)):
            if pattern is None or pattern.search(pkg) is None:
                modules.append(pkg)
            for info in iter_modules(
                    [f'{src_root}{sep}{pkg.replace(".", sep)}']):
                if not info.ispkg and (pattern is None
                                       or pattern.search(info.name) is None):
                    modules.append(pkg + '.' + info.name)

        sys.path.append(str(src_root))
        for module in modules:
            try:
                moduleObj = import_module(module)
                moduleFunctions = [
                    member for member in getmembers(moduleObj, isfunction)
                    if member[1].__module__ == moduleObj.__name__
                ]

                for fn in moduleFunctions:
                    result.append(
                        Function(module=module, name=fn[0],
                                 signature=signature(fn[1])))

            except ImportError as ex:
                logging.getLogger(__name__).error(
                    f'Error loading package {module}: {ex.msg}'
                )
    except ModuleNotFoundError as ex:
        logging.getLogger(__name__).error(
            f'{ex.msg}\n'
            + '\nYou are either missing it in your system,'
            + ' or you are using the scanner outside its virtual environment.\n'
        )
    finally:
        return result
