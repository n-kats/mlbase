"""
CLI引数を解釈するutilです。
"""
from argparse import ArgumentParser
from collections import OrderedDict
from typing import Any, List, Dict, NamedTuple


class _Args(NamedTuple):
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
        self.__args: List[_Args] = []
        self.__main_fn = None

    def start(self):
        """
        典型的な使い方のためのメソッド。
        コマンドライン引数をparseしてコマンドの内容を実行します。
        """
        parser = self.build()
        args = parser.parse_args()
        if hasattr(args, "handler"):
            args.handler(args)
        else:
            parser.print_help()

    def __call__(self, func):
        self.__main_fn = func

    def __rshift__(self, command: "Command"):
        self.__add_subcommand(command)
        return command

    def __lshift__(self, command: "Command"):
        return command >> self

    def option(self, *args, **kwargs):
        """
        引数を指定します。
        argparse.ArgumentParser.add_argumentと同じ引数です。
        """
        self.__args.append(_Args(args=args, kwargs=kwargs))

    def build(self, parser: ArgumentParser = None):
        """
        parserを作成します。
        引数にparserを指定するとそれに追加します。
        """
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

    def __add_subcommand(self, command: "Command"):
        self.__subcommands[command.name] = command
