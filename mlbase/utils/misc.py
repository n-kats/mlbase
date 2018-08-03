import sys
import os
from typing import NamedTuple, List, Optional
from pathlib import Path

import tensorflow as tf


def counting_iter(cnt):
    for i in range(1, cnt + 1):
        sys.stdout.write(f"{i}\r")
        yield i


def maybe_restore(sess: tf.Session, checkpoint: str, saver: tf.train.Saver):
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

    path = ToolPath(
        config=config,
        plugins=[],
        cache=cache,
        data=data,
        local=local,
        env=env)
    print(path)


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


get_tool_path()
