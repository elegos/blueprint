import argparse
import json
import os
from scanner.function import FunctionJSONEncoder
import subprocess
import sys
from os import environ
from os.path import abspath
import pickle

from scanner.moduleScanner import functionsScanner

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--package-path',
                        help='Package path to scan', required=True)
    parser.add_argument('--from-target-pipenv',
                        action='store_true', help='Skips pipenv check')
    args = parser.parse_args()

    packagePath: str = abspath(args.package_path)

    # Pipenv support
    pipfilePath = f'{packagePath}{os.path.sep}Pipfile'
    if not args.from_target_pipenv and os.path.isfile(pipfilePath):
        currentPath = os.path.dirname(os.path.realpath(__file__))

        pythonpath = environ.get('PYTHONPATH')
        pythonpath = pythonpath.split(':') if pythonpath else []
        pythonpath.append(currentPath)
        env = {**environ, 'PIPENV_IGNORE_VIRTUALENVS': '1',
               'PIPENV_PIPFILE': pipfilePath, 'PYTHONPATH': ':'.join(pythonpath)}

        runFromPipenvProc = subprocess.run(
            ['pipenv', 'run', 'python', sys.argv[0],
                '--from-target-pipenv', '-p', packagePath],
            cwd=currentPath,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print(runFromPipenvProc.stdout.decode('utf-8'))
    else:
        result = functionsScanner(packagePath, r'_test')
        print(pickle.dumps(result, protocol=3, fix_imports=True))
        # print(json.dumps(result, cls=FunctionJSONEncoder))
