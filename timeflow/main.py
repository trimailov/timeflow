import sys

from timeflow import parser


def main():
    args = parser.parse_args(sys.argv[1:])
    # if no command is passed, invoke help
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.parse_args(['--help'])
