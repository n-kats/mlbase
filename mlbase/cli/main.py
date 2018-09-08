import sys
from pathlib import Path
import subprocess
from typing import Dict, List

import yaml

from mlbase.utils.cli import Command, PluginManger, LocalPluginType
from mlbase.template.cifar.train import train_cifar_command
from mlbase.dataset.rough_estimate import rough_estimate_command
from mlbase.kaggle import kaggle_command

DEFAULT_EDITOR = "vi"


def build() -> Command:
    cmd = Command("mlbase", "機械学習を支援するコマンドです。")

    cmd_dataset = Command("dataset", "データセットに関するコマンドです。") << cmd
    cmd_dataset >> rough_estimate_command()

    cmd >> Command("research", "研究段階のもののコマンドです。") >> train_cifar_command()

    cmd >> kaggle_command()

    cmd >> Command("tree", "コマンドの一覧表示します。")(show_tree(cmd))

    # config
    config_file_map = {
        "mlbase": "~/.config/mlbase/mlbase.yml",
        "plugins": "~/.config/mlbase/plugins.yml",
    }
    config_edit = cmd >> Command("config", "設定を行います。") >> Command("edit", "エディタで編集を行います。")
    config_edit.option("target", choices=config_file_map.keys())

    @config_edit
    def config_edit_main(args):
        target = config_file_map[args.target]
        path = Path(target).expanduser()
        if not path.exists():
            path.parent.mkdir(exist_ok=True, parents=True)

        editor = DEFAULT_EDITOR
        config_path = Path(config_file_map["mlbase"]).expanduser()
        if config_path.exists():
            config = yaml.load(open(config_path))
            if isinstance(config, dict) and "editor" in config:
                editor = config["editor"]

        subprocess.Popen([editor, path]).wait()

    # plugin
    plugin_manager = PluginManger(cmd)
    plugin_manager.add_plugin_type("local", LocalPluginType)

    plugin_manager.load_yml("~/.config/mlbase/plugins.yml")
    cmd >> Command("plugins", "プラグインに関するもの") >> Command("update", "プラグインの更新をします。")(lambda _: plugin_manager.update())
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

        def __show(self, node: Command, output, is_used: set, depth=0, sep="  "):
            description = "上記参照" if node in is_used else node.doc
            print(f"{sep * depth}{node.name}: {description}", file=output)
            if node in is_used:
                return
            is_used.add(node)

            for child in node.subcommands:
                self.__show(child, depth=depth + 1, is_used=is_used, sep=sep, output=output)

    return lambda _: Tree(root).show()
