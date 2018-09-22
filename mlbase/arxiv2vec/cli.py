from mlbase.utils.cli import Command
from mlbase.arxiv2vec.actions import train, infer
from mlbase.arxiv2vec.dataset import json_arxiv, merge_json


def arxiv2vec_command():
    cmd = Command("arxiv2vec", "論文ベクトル化")
    cmd >> dataset_command()
    cmd >> infer_command()
    cmd >> train_command()

    return cmd


def dataset_command():
    """
    datasetコマンド
    """
    cmd = Command("dataset", "データセットを整理するコマンド")

    cmd_json = Command("json_arxiv", "arXivのデータを今回用に加工") << cmd
    cmd_json.option('--input', required=True, nargs='+')
    cmd_json.option('--output', required=True)

    @cmd_json
    def run_json_arxiv(args, *_, **__):
        json_arxiv.run(args.input, args.output)

    cmd_merge_json = Command("merge_json", "jsonファイルの統合") << cmd
    cmd_merge_json.option('--input', required=True, nargs='+')
    cmd_merge_json.option('--output', required=True)

    @cmd_merge_json
    def run_merge_json(args, *_, **__):
        merge_json(args.input, args.output)

    return cmd


def infer_command():
    """
    inferコマンド
    """
    cmd = Command("infer", "実行する")

    cmd_show_vector = Command("show_vector", "ベクトル表示") << cmd
    cmd_show_vector.option('--load_model')
    cmd_show_vector.option('input_texts', nargs="+")

    @cmd_show_vector
    def run_show_vector(args, *_, **__):
        model = infer.load_model(args.load_model)
        model.run_action("show_vector", model, args)

    cmd_compare = Command("compare", "比較") << cmd

    @cmd_compare
    def run_compare(args, *_, **__):
        model = infer.load_model(args.load_model)
        model.run_action("run_compare", model, args)

    cmd_find_neighbors = Command("find_neighbors", "近傍探索") << cmd
    cmd_find_neighbors.option("--train_data")

    @cmd_find_neighbors
    def run_find_neighbors(args, *_, **__):
        model = infer.load_model(args.load_model)
        model.run_action("run_find_neighbors", model, args)

    cmd_output_vectors = Command("output_vectors", "ベクトル保存") << cmd
    cmd_output_vectors.option("--load_model")
    cmd_output_vectors.option("--input_texts", nargs="+")

    @cmd_output_vectors
    def run_output_vectors(args, *_, **__):
        model = infer.load_model(args.load_model)
        model.run_action("run_output_vectors", model, args)

    return cmd


def train_command():
    """
    trainコマンド
    """
    cmd = Command("train", "訓練する")
    cmd.option("--model", required=True)
    cmd.option("--preprocess", required=True)
    cmd.option("--train_data", required=True)
    cmd.option("--save_model", required=True)
    cmd(train.run)
    return cmd
