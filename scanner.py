from os.path import abspath, dirname, sep
from src.moduleScanner import functionsScanner

if __name__ == '__main__':
    print('')
    print('')
    print('')
    print('')
    path = abspath(
        sep.join([dirname(__file__), '..', 'alperia-dp', 'glue', 'etl']))

    print(functionsScanner(path, r'_test'))
