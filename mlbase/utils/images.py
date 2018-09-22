from mlbase.lazy import numpy as np


def tiled_image(images: "np.ndarray"):
    n, h, w, ch = images.shape
    sq = int(np.ceil(np.sqrt(n)))
    output = np.zeros([sq * h, sq * w, ch], dtype=np.uint8)
    for i, image in enumerate(images):
        x = i % sq
        y = i // sq
        output[h * y:h * (y + 1), w * x:w * (x + 1)] = image
    return output
