"""General utility helpers."""

import numpy as np


def lighter(color, percent):
    color = np.array(color) * 255
    white = np.array([255, 255, 255])
    vector = white - color
    return tuple((color + vector * percent) / 255.0)
