import sys
from typing import Dict, List

from mlbase.utils.cli import Command, PluginManger, LocalPluginType
from mlbase.template.cifar.train import train_cifar_command
from mlbase.dataset.rough_estimate import rough_estimate_command


def build() -> Command:
    cmd = Command("mlbase", "機械学習を支援するコマンドです。")

    cmd_dataset = Command("dataset", "データセットに関するコマンドです。") << cmd
    cmd_dataset >> rough_estimate_command()

    cmd >> Command("research", "研究段階のもののコマンドです。") >> train_cifar_command()
    cmd / "research" >> Command("hoge", "hoge")

    cmd >> Command("tree", "コマンドの一覧表示")(show_tree(cmd))
    # cmd >> Command("plugins")
    plugin_manager = PluginManger(cmd)
    plugin_manager.add_plugin_type("local", LocalPluginType)

    plugin_manager.load_yml("~/.config/mlbase/plugins.yml")
    return cmd


def run():
    build().start()


def show_tree(root: Command):
    class Tree:
        def __init__(self, root: Command) -> None:
            self.__root = root
            self.__parent_to_children: Dict[Command, List[Command]] = {}

        def __add(self, parent: Command, child: Command):
            if parent in self.__parent_to_children:
                self.__parent_to_children[parent] = []

            self.__parent_to_children[parent].append(child)

        def show(self, output=sys.stdout):
            self.__show(self.__root, output=output, is_used=set())

        def __show(self,
                   node: Command,
                   output,
                   is_used: set,
                   depth=0,
                   sep="  "):
            description = "上記参照" if node in is_used else node.doc
            print(f"{sep * depth}{node.name}: {description}", file=output)
            if node in is_used:
                return
            is_used.add(node)

            for child in node.subcommands:
                self.__show(
                    child,
                    depth=depth + 1,
                    is_used=is_used,
                    sep=sep,
                    output=output)

    return lambda _: Tree(root).show()
