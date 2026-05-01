import numpy as np
import pytest
from numpy.testing import assert_array_equal


class TestQuickCluster:
    def test_single_pixel(self, gui):
        xlist = np.array([5])
        ylist = np.array([5])
        result = gui.quick_cluster(xlist, ylist, 5, 5)
        assert set(result) == {0}

    def test_adjacent_pixels(self, gui):
        xlist = np.array([0, 1])
        ylist = np.array([0, 0])
        result = gui.quick_cluster(xlist, ylist, 0, 0)
        assert set(result) == {0, 1}

    def test_diagonal_not_connected(self, gui):
        xlist = np.array([0, 1])
        ylist = np.array([0, 1])
        result = gui.quick_cluster(xlist, ylist, 0, 0)
        assert set(result) == {0}

    def test_l_shape(self, gui):
        xlist = np.array([0, 1, 2, 2, 2])
        ylist = np.array([0, 0, 0, 1, 2])
        result = gui.quick_cluster(xlist, ylist, 0, 0)
        assert set(result) == {0, 1, 2, 3, 4}

    def test_two_blobs(self, gui):
        xlist = np.array([0, 1, 5, 6])
        ylist = np.array([0, 0, 0, 0])
        result = gui.quick_cluster(xlist, ylist, 0, 0)
        assert set(result) == {0, 1}
