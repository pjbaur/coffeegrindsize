"""Cluster detection helpers."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

IntArray = NDArray[np.integer[Any]]
IntLike = int | np.integer[Any]


def quick_cluster(xlist: IntArray, ylist: IntArray, xstart: IntLike, ystart: IntLike) -> IntArray:
    """Flood-fill thresholded pixels using the legacy Manhattan-distance rule."""
    xcheck = np.array([xstart])
    ycheck = np.array([ystart])

    xlist_decay = np.copy(xlist)
    ylist_decay = np.copy(ylist)
    ilist_decay = np.arange(xlist.size)

    istart = np.where((xlist_decay == xstart) & (ylist_decay == ystart))
    if istart[0].size != 0:
        xlist_decay = np.delete(xlist_decay, istart[0])
        ylist_decay = np.delete(ylist_decay, istart[0])
        ilist_decay = np.delete(ilist_decay, istart[0])

    iout = istart[0]

    for _ in range(xlist.size):
        isel = np.where((np.abs(xlist_decay - xcheck[0]) + np.abs(ylist_decay - ycheck[0])) <= 1.001)

        if isel[0].size == 0:
            if xcheck.size == 1:
                break

            xcheck = np.delete(xcheck, 0)
            ycheck = np.delete(ycheck, 0)
            continue

        iout = np.append(iout, ilist_decay[isel[0]])

        xcheck = np.append(xcheck, xlist_decay[isel[0]])
        ycheck = np.append(ycheck, ylist_decay[isel[0]])

        xcheck = np.delete(xcheck, 0)
        ycheck = np.delete(ycheck, 0)

        if isel[0].size == xlist_decay.size:
            break

        xlist_decay = np.delete(xlist_decay, isel[0])
        ylist_decay = np.delete(ylist_decay, isel[0])
        ilist_decay = np.delete(ilist_decay, isel[0])

    return iout
