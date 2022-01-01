from argparse import ArgumentParser
from pathlib import Path
from blueprint.module_scanner import functions_scanner


def main():
    args = ArgumentParser()
    args.add_argument('package_root', help='root of the package to scan')
    args = args.parse_args()

    print('')
    print('')
    print('')
    print('')
    path = Path(args.package_root)

    print(functions_scanner(path.absolute(), r'_test'))


if __name__ == '__main__':
    main()
