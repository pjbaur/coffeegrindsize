"""Geometry helpers."""

from typing import Any

import numpy as np
import numpy.typing as npt


def smooth(x: npt.ArrayLike, window_size: int) -> npt.NDArray[Any]:
    window = np.ones(int(window_size)) / float(window_size)
    return np.convolve(x, window, "same")


def points_along_polygon(
    X_points: npt.NDArray[np.floating[Any]],
    Y_points: npt.NDArray[np.floating[Any]],
    X_polygon: npt.NDArray[np.floating[Any]],
    Y_polygon: npt.NDArray[np.floating[Any]],
) -> npt.NDArray[np.intp]:
    """Return indices of points within the pixel-width path of polygon edges."""
    nlines = X_polygon.size - 1
    x0 = X_points
    y0 = Y_points
    triggered = np.zeros(x0.size, dtype=bool)

    for li in range(nlines):
        x1 = X_polygon[li]
        y1 = Y_polygon[li]
        x2 = X_polygon[li + 1]
        y2 = Y_polygon[li + 1]

        ddline = np.abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / np.sqrt(
            (y2 - y1) ** 2 + (x2 - x1) ** 2
        )
        dd1 = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        dd2 = np.sqrt((x2 - x0) ** 2 + (y2 - y0) ** 2)
        dd12 = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        ipath = np.where((ddline <= np.sqrt(2.0) * 1.01) & (dd1 <= dd12) & (dd2 <= dd12))
        triggered[ipath[0]] = True

    return np.where(triggered)[0]
