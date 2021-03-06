from argparse import Namespace
import pickle
import json
from typing import (
    Optional,
    Callable,
    Dict,
    NewType,
    cast,
)

from mlbase.lazy import numpy as np

Model = NewType("Model", object)
_ACTIONS: Dict[str, Callable[[Model, Namespace], None]] = {}


def by_action_name(
    name: Optional[str] = None,
    actions: Dict[str, Callable[[Model, Namespace], None]] = _ACTIONS,
) -> Callable[[Callable], None]:
    def _action(fn: Callable):
        key: str = name or fn.__name__
        assert key not in _ACTIONS
        _ACTIONS[key] = fn

    return _action


def run_action(
    action_name: str,
    model: Model,
    args: Namespace,
):
    _ACTIONS[action_name](model, args)


def run(args: Namespace):
    model = load_model(args.load_model)
    run_action(args.infer_mode, model, args)


def load_model(path: str) -> Model:
    return cast(Model, pickle.load(open(path, "rb")))


@by_action_name()
def show_vector(model: Model, args: Namespace):
    """
    文章に対し評価し、そのベクトルを表示する
    """
    for input_ in args.input_texts:
        text = _get_input_text(input_)
        vec = model.infer_vector(text)
        print(input_)
        print(vec)


@by_action_name()
def compare(model: Model, args: Namespace):
    vec_l = model.infer_vector(_get_input_text(args.input_texts[0]))
    vec_r = model.infer_vector(_get_input_text(args.input_texts[1]))
    vec_l /= np.sqrt(sum(vec_l * vec_l))
    vec_r /= np.sqrt(sum(vec_r * vec_r))
    print("cos = ", sum(vec_r * vec_l))


@by_action_name()
def find_neighbors(model: Model, args: Namespace):
    """
    近傍探索を行う
    """
    targets = _load_train_data_to_show(args.train_data)
    for input_ in args.input_texts:
        print(f"--- INPUT: {input_}")
        print("".join(open(input_).readlines()))
        vec = model.infer_vector(_get_input_text(input_))
        top_scores = model.find_neighbors(vec)
        for order, (i, score) in enumerate(top_scores):
            print("---", order + 1, i, score)
            print(targets[i]["title"])
            print(targets[i]["id"])
            print(targets[i]["summary"][:160])


def _get_input_text(fname: str) -> str:
    return "".join(open(fname))


def _load_train_data_to_show(train_data: str):
    return json.load(open(train_data))


@by_action_name()
def output_vectors(model: Model, args: Namespace):
    """
    文章に対し評価し、そのベクトルを書き込む
    """
    texts = args.input_texts.copy()
    vectors = []
    for input_ in args.input_texts:
        text = _get_input_text(input_)
        vectors.append(model.infer_vector(text))
    vectors = np.array(vectors)
    np.savez(args.output_npz, texts=texts, vectors=vectors)
