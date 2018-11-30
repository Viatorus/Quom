import argparse
import sys
from pathlib import Path

from .quom import Quom


def main():
    parser = argparse.ArgumentParser(prog='quom', description='Single header library generator for C/C++.')
    parser.add_argument('input_path', metavar='input', type=Path, help='Input file path of the main header file.')
    parser.add_argument('output_path', metavar='output', type=Path,
                        help='Output file path of the generated single header file.')
    parser.add_argument('--stitch', metavar='format', type=str, default='~> stitch <~',
                        help='Format of the comment where the compilation units should be placed. \
                        Default: %(default)s')

    args = parser.parse_args()

    with args.output_path.open('w+') as file:
        Quom(args.input_path, file, args.stitch)


if __name__ == '__main__':
    sys.exit(main())