from pathlib import Path
import pickle


def cache_pickle(cache_path, func, args=[], kwargs={}):
    """
    関数の結果をpickleで保存し、そのファイルがあればそれを読み込む。
    Args:
        cache_path: 出力パス
        func: 実行関数
        args(list): 関数の引数
        kwargs(dict): 関数のキーワード引数
    """
    # 読み込み
    if cache_path is not None and Path(cache_path).exists():
        return pickle.load(open(cache_path, "rb"))

    # 作成
    result = func(*args, **kwargs)

    # 保存
    pickle.dump(result, open(cache_path, "wb"))

    return result
