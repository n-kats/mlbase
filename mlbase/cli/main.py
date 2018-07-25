from mlbase.utils.cli import Command
from mlbase.template.cifar.train import train_cifar_command


def run():
    cmd = Command("mlbase", "機械学習を支援するコマンドです。")

    cmd_dataset = Command("dataset", "データセットに関するコマンドです。") << cmd
    cmd_dataset.option("--input", help="入力データ")

    @cmd_dataset
    def _(args):
        print(args)

    cmd_research = Command("research", "研究段階のもののコマンドです。") << cmd
    train_cifar_command() << cmd_research

    cmd.start()
