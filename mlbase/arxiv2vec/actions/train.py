from mlbase.arxiv2vec.model import Doc2VecModel
from mlbase.arxiv2vec.preprocess import TeXMixedTextPreprocessor, SimplePreprocessor, AbsPreprocessor


def run(args, *_, **__):
    preprocesser = get_preprocessor(args.preprocess, args)
    model = get_model(args.model, preprocesser, args)
    train_docs = get_train_docs(args)
    model.train(train_docs)
    model.save(args.save_model)


def get_train_docs(args):
    return open(args.train_data)


def get_preprocessor(name, args) -> AbsPreprocessor:
    if name == "tex":
        return TeXMixedTextPreprocessor()
    elif name == "simple":
        return SimplePreprocessor()
    else:
        raise NotImplementedError()


def get_model(name, preprocesser, args):
    if name == "doc2vec":
        return Doc2VecModel(preprocesser)
    else:
        raise NotImplementedError()
