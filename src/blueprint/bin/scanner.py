from os.path import abspath, dirname, sep
from blueprint.moduleScanner import functionsScanner

def main():
    print('')
    print('')
    print('')
    print('')
    path = abspath(
        sep.join([dirname(__file__), '..', 'alperia-dp', 'glue', 'etl']))

    print(functionsScanner(path, r'_test'))

if __name__ == '__main__':
    main()
