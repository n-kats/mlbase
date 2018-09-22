import subprocess
from typing import Optional

from mlbase.utils.cli import Command, PluginManger, LocalPluginType
from mlbase.config import load_config, load_no_config, MLBaseConfig
from mlbase.note import note_command
from mlbase.template.cifar.train import train_cifar_command
from mlbase.dataset.rough_estimate import rough_estimate_command
from mlbase.kaggle import kaggle_command
from mlbase.arxiv2vec.cli import arxiv2vec_command
from mlbase.cli.tree import show_tree

META_CONFIG = ".meta:running:config"
META_NO_CONFIG = ".meta:running:no_config"


def run():
    args, _ = __entry_command().build(add_help=False).parse_known_args()
    config = __load_config(args)
    build(config).start()


def __load_config(args):
    no_config = getattr(args, META_NO_CONFIG)
    if no_config:
        return load_no_config()

    path = getattr(args, META_CONFIG)
    return load_config(path)


def __entry_command():
    cmd = Command("mlbase", "機械学習を支援するコマンドです。")
    cmd.option("--config", dest=META_CONFIG, help="設定ファイルのパス")
    cmd.option("--no_config", action="store_true", dest=META_NO_CONFIG, help="設定ファイルを用いない。--configよりも優先される。")
    # cmd.option("--interactive", action="store_true", dest=META_INTERACTIVE, help="対話モード")
    return cmd


def build(config: Optional[MLBaseConfig] = None) -> Command:
    if config is None:
        config = load_config()

    cmd = __entry_command()

    cmd >> note_command()
    cmd >> kaggle_command()

    cmd_dataset = Command("dataset", "データセットに関するコマンドです。") << cmd
    cmd_dataset >> rough_estimate_command()

    cmd >> Command("research", "研究段階のもののコマンドです。") >> train_cifar_command()

    cmd >> arxiv2vec_command()

    cmd >> Command("tree", "コマンドの一覧表示します。")(show_tree(cmd))

    # config
    config_file_map = {
        "mlbase": config.mlbase_config,
        "plugins": config.plugin_config,
    }
    config_edit = cmd >> Command("config", "設定を行います。") >> Command("edit", "エディタで編集を行います。")
    config_edit.option("target", choices=config_file_map.keys())

    @config_edit
    def config_edit_main(args):
        path = config_file_map[args.target]
        if not path.exists():
            path.parent.mkdir(exist_ok=True, parents=True)

        subprocess.Popen([*config.editor, path]).wait()

    # plugin
    plugin_manager = PluginManger(cmd)
    plugin_manager.add_plugin_type("local", LocalPluginType)

    plugin_manager.load_yml(config.plugin_config)
    cmd >> Command("plugins", "プラグインに関するもの") >> Command("update", "プラグインの更新をします。")(lambda _: plugin_manager.update())
    return cmd
