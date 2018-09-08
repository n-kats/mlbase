import subprocess

from mlbase.utils.cli import Command


def kaggle_command():
    cmd = Command("kaggle", "kaggleコマンドを実行する")
    cmd.option("args", nargs="*")

    @cmd
    def kaggle_main(options):
        sub = subprocess.Popen(["kaggle", *options.args])
        sub.wait()

    return cmd
