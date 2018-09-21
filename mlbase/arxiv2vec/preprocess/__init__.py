from abc import ABCMeta, abstractmethod
from typing import List, Iterator

from mlbase.lazy import gensim
from mlbase.arxiv2vec.preprocess.tex_doc import split_tex_doc


def simple_preprocess(*args, **kwargs):
    return gensim.utils.simple_preprocess(*args, **kwargs)


class AbsPreprocessor(metaclass=ABCMeta):
    @abstractmethod
    def preprocess(self, line: str) -> List[str]:
        pass


class SimplePreprocessor(AbsPreprocessor):
    def __init__(self, deacc: bool = False, min_len: int = 2, max_len: int = 15) -> None:
        self.__deacc = deacc
        self.__min_len = min_len
        self.__max_len = max_len

    def preprocess(self, line: str) -> List[str]:
        return simple_preprocess(deacc=self.__deacc, min_len=self.__min_len, max_len=self.__max_len)


class TeXMixedTextPreprocessor(AbsPreprocessor):
    """
    $で囲まれた範囲を一つの単語とみなす
    """

    def __init__(self,):
        pass

    def __tokenize(self, line: str) -> Iterator[str]:
        return split_tex_doc(line)

    def __fix_token(self, token: str) -> str:
        token = token.lower()
        if token[-1] in ",.":
            token = token[:-1]
        return token

    def __accept(self, token: str) -> bool:
        return True

    def preprocess(self, line: str) -> List[str]:
        tokens = self.__tokenize(line)
        tokens = map(self.__fix_token, tokens)
        tokens = filter(self.__accept, tokens)
        return list(tokens)
