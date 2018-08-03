"""
CLI引数を解釈するutilです。
"""
from argparse import ArgumentParser
from collections import OrderedDict
from typing import Any, List, Dict, NamedTuple, Callable, Optional
from abc import ABC, abstractmethod
import importlib
import pathlib

import yaml


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
        return self

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

    @property
    def subcommands(self):
        """
        Return: subcommandのリスト
        """
        return list(self.__subcommands.values())

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


class PluginManger:
    def __init__(self, command: Command) -> None:
        """
        Args:
            command(Command): プラグインからサブコマンドを生やす用
        """
        self.__command = command
        self.__plugin_types: Dict[str, "AbstractPlugin"] = {}

    def add_plugin_type(self, name, type_):
        assert name not in self.__plugin_types
        self.__plugin_types[name] = type_

    def load_yml(self, path):
        for obj in yaml.load(open(pathlib.Path(path).expanduser())):
            type_name = obj.get("type")
            args = obj.get("args")
            kwargs = obj.get("kwargs")
            if type_name not in self.__plugin_types:
                raise Exception("unknown plugin_type")

            plugin = self.get_plugin(type_name, args, kwargs)
            plugin.load(self, self.__command)

    def get_plugin(self, type_name, args, kwargs):
        args = [] if args is None else args
        kwargs = {} if kwargs is None else kwargs

        return self.__plugin_types[type_name](*args, **kwargs)


class PluginMangerWrapper:
    def __init__(self, plugin_manager: PluginManger) -> None:
        self.__plugin_manager = plugin_manager

    def add_plugin_type(self, name, type_):
        self.__plugin_manager.add_plugin_type(name, type_)


class AbstractPlugin(ABC):
    @abstractmethod
    def on_load(self, plugin_manager: PluginMangerWrapper, command: Command):
        pass


class AbstractPluginType(ABC):
    @abstractmethod
    def load(self, plugin_manager: PluginMangerWrapper, command: Command):
        pass


class LocalPluginType(AbstractPluginType):
    def __init__(self, path, plugin) -> None:
        path = pathlib.Path(path).expanduser()
        path = "plugin_foo/plugin.py"
        module_spec = importlib.util.spec_from_file_location(
            f"LocalPluginType:{path}", path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        self.__plugin_class = getattr(module, plugin)

    def load(self, plugin_manager: PluginMangerWrapper, command: Command):
        """
        AbstractPluginのインターフェイスを持つクラスをロードする
        """
        plugin = self.__plugin_class()
        plugin.on_load(plugin_manager, command)
