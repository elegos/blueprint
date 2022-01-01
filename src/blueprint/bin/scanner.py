from os.path import abspath, dirname, sep
from blueprint.module_scanner import functions_scanner


def main():
    print('')
    print('')
    print('')
    print('')
    path = abspath(
        sep.join([dirname(__file__), '..', 'alperia-dp', 'glue', 'etl']))

    print(functions_scanner(path, r'_test'))


if __name__ == '__main__':
    main()
