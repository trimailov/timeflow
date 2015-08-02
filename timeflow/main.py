import sys

from timeflow import arg_parser


def main():
    args = arg_parser.parse_args(sys.argv[1:])
    # if no command is passed, invoke help
    if hasattr(args, 'func'):
        args.func(args)
    else:
        arg_parser.parse_args(['--help'])
