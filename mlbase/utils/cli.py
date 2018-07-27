"""
CLI引数を解釈するutilです。
"""
from argparse import ArgumentParser
from collections import OrderedDict
from typing import Any, List, Dict, NamedTuple, Callable, Optional


class _Args(NamedTuple):
    args: List[Any]
    kwargs: Dict[str, Any]


class _Meta(NamedTuple):
    parser: ArgumentParser
    handler: Optional[Callable]


class Command:
    """
    >>> cmd = Command("sample", "例のコマンド")
    >>> foo = Command("foo", "fooコマンド") << cmd
    >>> foo.option("--input")
    >>> foo(lambda args: print("foo"))
    >>> (cmd / "foo") == foo
    True
    >>> x = cmd.build()

    """

    def __init__(self, name, doc, metakey="command_meta"):
        """
        Args:
            name(str): コマンド名
            doc(str): コマンド説明
            metakey(str): コマンドに付随する情報をパース結果につける際のプロパティ名。関連するコマンド間で同じものを指定する。
        """
        self.name = name
        self.doc = doc
        self.__metakey = metakey
        self.__subcommands: Dict[str, Command] = OrderedDict()
        self.__args: List[_Args] = []
        self.__main_fn = None

    def has_metakey(self, key):
        """
        メタキーが等しいことを確認する
        """
        return self.__metakey == key

    def start(self):
        """
        典型的な使い方のためのメソッド。
        コマンドライン引数をparseしてコマンドの内容を実行します。
        """
        parser = self.build()
        args = parser.parse_args()
        meta: _Meta = getattr(args, self.__metakey)
        if meta.handler is None:
            meta.parser.print_help()
        else:
            meta.handler(args)

    def __call__(self, func):
        self.__main_fn = func

    def __rshift__(self, command: "Command") -> "Command":
        self.__add_subcommand(command)
        return command

    def __lshift__(self, command: "Command") -> "Command":
        return command >> self

    def __truediv__(self, command_name: str) -> Optional["Command"]:
        return self.__get_subcommand(command_name)

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

        handler = None if self.__subcommands else self.__main_fn
        meta = _Meta(parser=parser, handler=handler)
        parser.set_defaults(**{self.__metakey: meta})
        return parser

    def __add_args(self, parser: ArgumentParser):
        for args, kwargs in self.__args:
            parser.add_argument(*args, **kwargs)

    def __add_subcommand(self, command: "Command"):
        assert command.has_metakey(self.__metakey)
        assert command.name not in self.__subcommands, Exception(
            f"コマンド{command.name}が重複しています")
        self.__subcommands[command.name] = command

    def __get_subcommand(self, name: str) -> Optional["Command"]:
        return self.__subcommands.get(name)
