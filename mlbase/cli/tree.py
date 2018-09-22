import sys
from typing import Dict, List
from mlbase.utils.cli import Command


class _Tree:
    def __init__(self, root: Command) -> None:
        self.__root = root
        self.__parent_to_children: Dict[Command, List[Command]] = {}

    def __add(self, parent: Command, child: Command):
        if parent in self.__parent_to_children:
            self.__parent_to_children[parent] = []

        self.__parent_to_children[parent].append(child)

    def show(self, output=sys.stdout):
        self.__show(self.__root, output=output, is_used=set())

    def __show(self, node: Command, output, is_used: set, depth=0, sep=">   "):
        description = "上記参照" if node in is_used else node.doc
        print(f"{sep * depth}{node.name}: {description}", file=output)
        if node in is_used:
            return
        is_used.add(node)

        for child in node.subcommands:
            self.__show(child, depth=depth + 1, is_used=is_used, sep=sep, output=output)


def show_tree(root: Command):
    return lambda *_, **__: _Tree(root).show()
