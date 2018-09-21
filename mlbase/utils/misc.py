import sys
import os
from typing import NamedTuple, List, Optional
from pathlib import Path
import importlib

_LAZY_MODULES = {}
_LOADED_MODULES = {}


class LazyModule:
    def __init__(self, module):
        _LAZY_MODULES[self] = module
        _LOADED_MODULES[self] = None

    def __getattribute__(self, name):
        if _LOADED_MODULES[self] is None:
            _LOADED_MODULES[self] = importlib.import_module(_LAZY_MODULES[self])
        return getattr(_LOADED_MODULES[self], name)


def lazy(module):
    return LazyModule(module)


tf = lazy("tensorflow")


def plugin_root(path):
    """
    パスを追加する。
    プラグインで呼び出すことを推奨する。

    >>> plugin_root(__file__)
    """
    path = Path(path)
    path = path.parent if path.is_file else path
    sys.path.append(str(path))


def counting_iter(cnt):
    for i in range(1, cnt + 1):
        sys.stdout.write(f"{i}\r")
        yield i


def maybe_restore(sess, checkpoint: str, saver):
    if checkpoint:
        saver.restore(sess, checkpoint)
    else:
        sess.run(tf.global_variables_initializer())


class ToolPath(NamedTuple):
    config: Path
    cache: Path
    data: Path
    plugins: List[Path]
    local: Optional[Path]
    env: Optional[Path]


def get_tool_path(name="mlbase"):
    user = Path.home()
    config = user / ".config" / name
    data = user / ".local/shape" / name
    cache = user / ".cache" / name

    local = find_dir_upto_root(f".{name}", Path.cwd())
    env_varname = f"{name.upper()}_PATH"
    env = os.getenv(env_varname)

    path = ToolPath(config=config, plugins=[], cache=cache, data=data, local=local, env=env)
    # print(path)
    return path


def iter_upto_root(path):
    path = Path(path)
    yield path
    while path != path.parent:
        path = path.parent
        yield path


def find_dir_upto_root(name, cwd) -> Optional[Path]:
    for path in iter_upto_root(cwd):
        target = path / name
        if target.exists():
            return target

    return None


def print_tree(obj, output=sys.stdout):
    def _print_tree(obj, depth):
        indent = "  " * depth
        for k, v in obj.items():
            if isinstance(v, dict):
                print(f"{indent}{k}:", file=output)
                _print_tree(v, depth + 1)

            else:
                print(f"{indent}{k}: {v}", file=output)

    _print_tree(obj, 0)
