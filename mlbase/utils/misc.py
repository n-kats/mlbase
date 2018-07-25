import sys

import tensorflow as tf


def counting_iter(cnt):
    for i in range(1, cnt + 1):
        sys.stdout.write(f"{i}\r")
        yield i


def maybe_restore(sess: tf.Session, checkpoint: str, saver: tf.train.Saver):
    if checkpoint:
        saver.restore(sess, checkpoint)
    else:
        sess.run(tf.global_variables_initializer())
