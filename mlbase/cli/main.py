from mlbase.utils.cli import Command
from mlbase.template.cifar.train import train_cifar_command
from mlbase.dataset.rough_estimate import rough_estimate_command


def run():
    cmd = Command("mlbase", "機械学習を支援するコマンドです。")

    cmd_dataset = Command("dataset", "データセットに関するコマンドです。") << cmd
    rough_estimate_command() << cmd_dataset

    cmd_research = Command("research", "研究段階のもののコマンドです。") << cmd
    train_cifar_command() << cmd_research

    cmd.start()
