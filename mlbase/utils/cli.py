from argparse import ArgumentParser
from collections import OrderedDict
from typing import Any, List, Dict, NamedTuple


class Args(NamedTuple):
    args: List[Any]
    kwargs: Dict[str, Any]


class Command:
    """
    >>> cmd = Command("sample", "例のコマンド")
    >>> foo = Command("foo", "fooコマンド") << cmd
    >>> foo.option("--input")
    >>> @foo
        def main(args):
            print(args)
    >>> parser = cmd.build()
    >>> args = parser.parse_args()
    >>> if hasattr(args, "handler"):
            args.handler(args)
    """

    def __init__(self, name, doc):
        self.name = name
        self.doc = doc
        self.__subcommands: Dict[str, Command] = OrderedDict()
        self.__args: List[Args] = []
        self.__main_fn = None

    def start(self):
        parser = self.build()
        args = parser.parse_args()
        if hasattr(args, "handler"):
            args.handler(args)
        else:
            parser.print_help()

    def __call__(self, func):
        self.__main_fn = func

    def __rshift__(self, command: "Command"):
        self.__subcommands[command.name] = command
        return command

    def __lshift__(self, command: "Command"):
        return command >> self

    def option(self, *args, **kwargs):
        self.__args.append(Args(args=args, kwargs=kwargs))

    def build(self, parser: ArgumentParser = None):
        if parser is None:
            parser = ArgumentParser(
                prog=self.name, description=self.doc, allow_abbrev=False)
        self.__add_args(parser)

        if self.__subcommands:
            subparsers = parser.add_subparsers(dest=self.name)
            for cmd in self.__subcommands.values():
                sub = subparsers.add_parser(cmd.name, description=cmd.doc)
                cmd.build(sub)
        elif self.__main_fn is not None:
            parser.set_defaults(handler=self.__main_fn)

        return parser

    def __add_args(self, parser: ArgumentParser):
        for args, kwargs in self.__args:
            parser.add_argument(*args, **kwargs)
