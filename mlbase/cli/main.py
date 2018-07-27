from mlbase.utils.cli import Command
from mlbase.template.cifar.train import train_cifar_command
from mlbase.dataset.rough_estimate import rough_estimate_command


def run():
    cmd = Command("mlbase", "機械学習を支援するコマンドです。")

    cmd_dataset = Command("dataset", "データセットに関するコマンドです。") << cmd
    cmd_dataset >> rough_estimate_command()

    cmd >> Command("research", "研究段階のもののコマンドです。") >> train_cifar_command()
    cmd / "research" >> Command("hoge", "hoge")
    cmd.start()
