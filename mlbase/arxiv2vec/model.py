import pickle
from typing import Iterator

from mlbase.lazy import gensim


def get_doc2vec(*args, **kwargs):
    return gensim.models.Doc2Vec(*args, **kwargs)


def get_tagged_document(*args, **kwargs):
    return gensim.models.doc2vec.TaggedDocument(*args, **kwargs)


class Doc2VecModel:
    def __init__(self, preprocessor):
        self.__preprocessor = preprocessor
        self.__model = None

    def train(self, train_docs: Iterator[str]):
        train_corpus = [
            get_tagged_document(self.__preprocessor.preprocess(txt),
                                [i]) for i, txt in enumerate(train_docs)
        ]
        model = get_doc2vec(size=50)
        model.build_vocab(train_corpus)
        model.train(train_corpus, total_examples=model.corpus_count, epochs=500)
        self.__model = model

    def save(self, path: str):
        # ディレクトリ作成
        pickle.dump(self, open(path, "wb"))

    def infer_vector(self, text: str):
        input_ = self.__preprocessor.preprocess(text)
        return self.__model.infer_vector(input_, steps=50)

    def find_neighbors(self, vec):
        return self.__model.docvecs.most_similar([vec])


def load(path: str):
    return pickle.load(open(path, "rb"))


def infer(model, document):
    pass
