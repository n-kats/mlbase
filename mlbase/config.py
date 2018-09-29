"""
ユーザー情報を管理する。
ユーザーはデータ等のリソースをもち、リソースから新しいリソースを作成する。

リソースはどのような経緯のものかの情報をもつ。これは、
* リソースの出所
* ソフトウェアによる変換過程
* 初期状態との変更の有無（初期のハッシュ値）
* バージョン情報
"""
from typing import NamedTuple, List
from pathlib import Path

import yaml

from mlbase.logger import error

DEFAULT_MLBASE_CONFIG = "~/.config/mlbase/mlbase.yml"
DEFAULT_PLUGINS_CONFIG = "~/.config/mlbase/plugins.yml"
DEFAULT_STORAGE = "~/.local/share/mlbase"
DEFAULT_EDITOR = "vi"


class Indentification(NamedTuple):
    pass


class Resource(NamedTuple):
    source: object
    versin: object


class MLBaseConfig(NamedTuple):
    editor: List[str]
    storage: Path
    mlbase_config: Path
    plugin_config: Path

    @classmethod
    def load(cls, filepath):
        path = Path(filepath).expanduser()
        if not path.exists():
            raise Exception("設定ファイルが存在しません。")

        config = yaml.load(open(path))
        if not isinstance(config, dict):
            raise Exception("設定ファイルの形式が間違っています。")

        editor = config.get("editor", DEFAULT_EDITOR)
        if not isinstance(editor, list):
            editor = [editor]

        return cls(
            editor=editor,
            mlbase_config=path,
            plugin_config=Path(config.get("plugin_config", DEFAULT_PLUGINS_CONFIG)).expanduser(),
            storage=Path(config.get("storage", DEFAULT_STORAGE)).expanduser()
        )

    @classmethod
    def get_default(cls, config=None) -> "MLBaseConfig":
        if config is None:
            config = Path(DEFAULT_MLBASE_CONFIG).expanduser()

        return cls(
            editor=[DEFAULT_EDITOR],
            mlbase_config=Path(config).expanduser(),
            plugin_config=Path(DEFAULT_PLUGINS_CONFIG).expanduser(),
            storage=Path(DEFAULT_STORAGE).expanduser()
        )


def load_no_config():
    return MLBaseConfig.get_default()


def load_config(config=None) -> MLBaseConfig:
    if config is None:
        config = DEFAULT_MLBASE_CONFIG
    try:
        return MLBaseConfig.load(config)
    except Exception as e:
        error(f"{config}を修正してくだい")
        conf = MLBaseConfig.get_default(config=config)
        return conf
