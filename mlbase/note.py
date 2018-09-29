from pathlib import Path
from typing import NamedTuple, List
from subprocess import Popen

from mlbase.utils.cli import Command
from mlbase.config import MLBaseConfig


class NoteObject(NamedTuple):
    name: str
    message: str
    tags: List[str]
    storage: Path
    entory_point: Path
    edit_command: str

    def add(self):
        pass


def __add_note(note: NoteObject):
    print(f"{note.name}\t{note.storage}\t{note.entory_point}\t{note.edit_command}\t{note.message}")
    tags = [] if note.tags is None else note.tags
    print(f"{note.name}\t{tags}")
    cmd = note.edit_command.format(editor="vim", entory_point=note.entory_point)
    print(f"$ {cmd}")


def note_command():
    cmd = Command("note", "ノートを書く")

    # add
    add_cmd = Command("add", "追加する") << cmd
    add_cmd.option("--name", required=True, help="名前")
    add_cmd.option("--message", required=True, help="説明")
    add_cmd.option("--storage", help="保存先")
    add_cmd.option("--tags", nargs="*", help="タグ")
    add_cmd.option("--entory_point", required=True, help="編集時に開く対象")
    add_cmd.option("--edit_command", default="{editor} {entory_point}", help="編集コマンド")

    @add_cmd
    def _(args, config: MLBaseConfig, *_, **__):
        note = NoteObject(
            name=args.name,
            message=args.message,
            tags=args.tags,
            storage=args.storage or config.storage,
            entory_point=args.entory_point,
            edit_command=args.edit_command.format(editor=config.editor)
        )
        __add_note(note)

    # edit
    edit_cmd = Command("edit", "編集する") << cmd
    edit_cmd.option("name")

    @edit_cmd
    def run_edit(args, config: MLBaseConfig, *_, **__):
        pass

    # remove
    remove_cmd = Command("remove", "消す（隠す）") << cmd
    remove_cmd.option("name")

    @remove_cmd
    def run_remove(args, *_, **__):
        pass

    # show
    show_cmd = Command("show", "一覧する") << cmd
    show_cmd.option("--tag")

    @show_cmd
    def run_show(args, *_, **__):
        pass

    return cmd


def arxiv_command():
    cmd_arxiv = Command("arxiv", "arXivの論文を管理")
    cmd_arxiv_add = cmd_arxiv >> Command("add", "論文を追加する")
    cmd_arxiv_remove = cmd_arxiv >> Command("remove", "論文を削除する")


"""
$ mlbase note add --name arxiv_XXXX_YYYYY --message "some message" --storage ~/path/to/notes_dir --tags tag1 tag2 tag3
$ mlbase arxiv add https://arxiv.org/abs/XXXX.YYYYY
# update ~/.local/share/mlbase/notes/list.jsonl
arxiv_XXXX.YYYYY

$ mlbase arxiv add --rm https://arxiv.org/abs/XXXX.YYYYY
# 古いノートを消して追加する
arxiv_XXXX_YYYYY

$ mlbase arxiv edit XXXX.YYYYY
# edit ~/.local/share/mlbase/notes/arxiv_XXXX_YYYYY/note.md

$ mlbase arxiv show
arxiv_XXXX_YYYYY
...

$ mlbase arxiv remove XXXX.YYYYY
# meta:hideタグをつける
"""
