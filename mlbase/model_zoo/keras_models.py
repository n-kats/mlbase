from mlbase.lazy import tensorflow as tf


def get_model(model, model_kwargs=None):
    if model_kwargs is None:
        model_kwargs = {}
    return getattr(tf.keras.applications, model)(**model_kwargs)
