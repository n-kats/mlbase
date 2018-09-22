import sys
from typing import NamedTuple, List
import itertools as it
from importlib import import_module
from pathlib import Path

import mlbase.hyper_param as hp
from mlbase.utils.cli import Command
from mlbase.model_interface import ModelInterface, Role
from mlbase.utils.cache import cache_pickle
from mlbase.utils.misc import counting_iter, maybe_restore
from mlbase.lazy import (
    tensorflow as tf,
    numpy as np,
)


class Data(NamedTuple):
    images: "np.ndarray"
    coarse_labels: "np.ndarray"
    fine_labels: "np.ndarray"


class MetaData(NamedTuple):
    coarse_labels: List[str]
    fine_labels: List[str]
    train_data_count: int
    test_data_count: int


class DataSet(NamedTuple):
    train: Data
    test: Data
    meta: MetaData


def load(data_dir) -> DataSet:
    coarse_labels_path = Path(data_dir) / 'coarse_label_names.txt'
    fine_labels_path = Path(data_dir) / 'fine_label_names.txt'
    test_path = Path(data_dir) / 'test.bin'
    train_path = Path(data_dir) / 'train.bin'

    train_data = load_image_binary(train_path)
    test_data = load_image_binary(test_path)
    meta = load_meta_data(coarse_labels_path, fine_labels_path, train_data, test_data)
    return DataSet(train=train_data, test=test_data, meta=meta)


def load_meta_data(coarse_labels_path, fine_labels_path, train_data: Data, test_data: Data) -> MetaData:
    coarse_labels = [l.rstrip() for l in open(coarse_labels_path)]
    fine_labels = [l.rstrip() for l in open(fine_labels_path)]
    train_data_count = len(train_data.images)
    test_data_count = len(test_data.images)
    return MetaData(
        coarse_labels=coarse_labels,
        fine_labels=fine_labels,
        train_data_count=train_data_count,
        test_data_count=test_data_count
    )


def load_image_binary(path) -> Data:
    clabels = []
    flabels = []
    images = []
    with open(path, 'rb') as f:
        for i in it.count():
            data = f.read(32 * 32 * 3 + 2)
            if not data:
                break
            sys.stdout.write(f"{i}\r")
            clabel = data[0]
            flabel = data[1]
            image = list(data[2:])
            clabels.append(clabel)
            flabels.append(flabel)
            images.append(image)
    clabels = np.array(clabels)
    flabels = np.array(flabels)
    images_np = np.array(images, dtype=np.uint8)
    images_np = images_np.reshape([-1, 3, 32, 32]).transpose([0, 2, 3, 1])
    return Data(images=images_np, coarse_labels=clabels, fine_labels=flabels)


def batchnizer(data: Data, batch_size, total_count):
    while True:
        ids = np.random.randint(total_count, size=[batch_size])
        yield data.images[ids], data.coarse_labels[ids], data.fine_labels[ids]


def batchnizer_in_order(data: Data, batch_size, total_count):
    assert total_count >= 0
    assert batch_size > 0
    head = 0
    tail = batch_size
    while True:
        ids = range(head, tail)
        yield data.images[ids], data.coarse_labels[ids], data.fine_labels[ids]
        if tail == total_count:
            break
        head = tail
        tail = min(head + batch_size, total_count)


class ScoreStore:
    def __init__(self):
        self.__positive = 0
        self.__negative = 0

    def add(self, score):
        self.__positive += score.positive
        self.__negative += score.negative

    @property
    def accuracy(self):
        total = self.__positive + self.__negative
        return np.nan if total == 0 else self.__positive / total


def validate(sess, test_data: Data, meta: MetaData, score, model_if):
    test_batch = batchnizer_in_order(test_data, 10, meta.test_data_count)
    test_score = ScoreStore()
    for img, label_c, label_f in test_batch:
        feed_dict = model_if.feed_dict(
            {
                "input_images": img,
                "coarse_labels": label_c,
                "fine_labels": label_f,
                "is_training": False,
            }
        )

        test_score.add(sess.run(score, feed_dict))
    return test_score.accuracy


def get_cifar_interface():
    model_if = ModelInterface("CifarClassification")
    model_if.add("input_images", tf.float32, [None, 32, 32, 3], "入力画像", Role.INPUT)
    model_if.add("coarse_labels", tf.int64, [None], "10クラス分類の教師", Role.GROUND_TRUTH)
    model_if.add("fine_labels", tf.int64, [None], "100クラス分類の教師", Role.GROUND_TRUTH)
    model_if.add("is_training", tf.bool, [], "訓練時かのフラグ", Role.HAS_DEFAULT)
    model_if.add("learning_rate", tf.float32, [], "学習率", Role.TRAIN_ONLY)
    return model_if


def __apply_if_to_module(model_if, module):
    x = model_if.get("input_images")
    y_c = model_if.get("coarse_labels")
    y_f = model_if.get("fine_labels")
    is_training = model_if.get("is_training")
    lr = model_if.get("learning_rate")

    y = module.inference(x, is_training)
    train = module.training(module.loss(y, y_f, y_c), lr)
    score = module.scoring(y, y_f, y_c)
    return train, score


def run(args):
    hp.open_hyper_param(args.param)
    dataset: DataSet = cache_pickle(cache_path=args.cache_path, args=[args.data_path], func=load)

    model_if = get_cifar_interface()
    module = hp.get_hyper_param("model", dtype=import_module)
    train, score = __apply_if_to_module(model_if, module)

    saver = tf.train.Saver()
    save_file = args.output
    train_batch = batchnizer(dataset.train, 50, dataset.meta.train_data_count)

    with tf.Session() as sess:
        maybe_restore(sess, args.checkpoint, saver)

        lr_ = hp.get_hyper_param("learning_rate")
        total_step = hp.get_hyper_param("total_step")

        for i in counting_iter(total_step):
            img, label_c, label_f = next(train_batch)
            feed_dict = model_if.feed_dict(
                {
                    "input_images": img,
                    "coarse_labels": label_c,
                    "fine_labels": label_f,
                    "is_training": True,
                    "learning_rate": lr_
                }
            )

            sess.run(train, feed_dict)
            if i % 2000 == 0:
                val = validate(sess, dataset.test, dataset.meta, score, model_if)
                print(i, val)
            if i % 100000 == 0:
                lr_ *= 0.2
            if i % 10000 == 0:
                saver.save(sess, save_file)


def train_cifar_command() -> Command:
    cmd = Command("train_cifar", "cifar100の訓練")
    cmd(run)
    cmd.option("--checkpoint")
    cmd.option("--data_path", required=True, type=Path, help="~/data/cifar-100-binary")
    cmd.option("--cache_path", default="_cifar100_cache.pkl")
    cmd.option("--output", required=True)
    cmd.option("--param", required=True)
    return cmd


def main():
    train_cifar_command().start()


if __name__ == '__main__':
    main()
