from mlbase.utils.cli import Command


def run():
    cmd = Command("mlbase", "機械学習を支援するコマンドです。")

    cmd_dataset = Command("dataset", "データセットに関するコマンドです。") << cmd
    cmd_dataset.option("--input", help="入力データ")

    @cmd_dataset
    def _(args):
        print(args)

    cmd.start()
