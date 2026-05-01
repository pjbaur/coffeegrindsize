import numpy as np
import pytest
from numpy.testing import assert_allclose


class TestSmooth:
    def test_smooth_impulse(self, gui):
        x = np.array([0, 0, 0, 1, 0, 0, 0], dtype=float)
        result = gui.smooth(x, 3)
        expected = np.array([0, 0, 1 / 3, 1 / 3, 1 / 3, 0, 0])
        assert_allclose(result, expected, atol=1e-10)

    def test_smooth_uniform(self, gui):
        x = np.array([1, 1, 1, 1, 1], dtype=float)
        result = gui.smooth(x, 3)
        expected = np.array([2 / 3, 1, 1, 1, 2 / 3])
        assert_allclose(result, expected, atol=1e-10)

    def test_smooth_ramp(self, gui):
        x = np.array([1, 2, 3, 4, 5], dtype=float)
        result = gui.smooth(x, 3)
        expected = np.array([1.0, 2.0, 3.0, 4.0, 3.0])
        assert_allclose(result, expected, atol=1e-10)

    def test_smooth_window_1(self, gui):
        x = np.array([1, 2, 3, 4], dtype=float)
        result = gui.smooth(x, 1)
        assert_allclose(result, x)

    def test_smooth_window_larger_than_data(self, gui):
        x = np.array([1, 2, 3], dtype=float)
        result = gui.smooth(x, 5)
        assert result.shape[0] >= 3
        assert not np.any(np.isnan(result))


class TestWeightedStddev:
    def test_equal_weights_frequency_unbiased(self, gui):
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        weights = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        result = gui.weighted_stddev(data, weights, frequency=True, unbiased=True)
        assert_allclose(result, np.sqrt(2.5), atol=1e-10)

    def test_biased(self, gui):
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        weights = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        result = gui.weighted_stddev(data, weights, frequency=True, unbiased=False)
        expected = np.std(data)
        assert_allclose(result, expected, atol=1e-10)

    def test_mutates_weights_known_bug(self, gui):
        data = np.array([1.0, 2.0])
        weights = np.array([2.0, 3.0])
        weights_copy = weights.copy()
        gui.weighted_stddev(data, weights, frequency=True, unbiased=True)
        assert not np.array_equal(weights, weights_copy)


class TestAttainableMassSimulate:
    def test_tiny_particle(self, gui):
        r = 0.05
        volume = 4.0 / 3.0 * np.pi * r**3
        volumes = np.array([volume])
        result = gui.attainable_mass_simulate(volumes)
        assert_allclose(result[0], volume, atol=1e-15)

    def test_boundary_particle(self, gui):
        r = 0.1
        volume = 4.0 / 3.0 * np.pi * r**3
        volumes = np.array([volume])
        result = gui.attainable_mass_simulate(volumes)
        assert_allclose(result[0], volume, atol=1e-15)

    def test_large_particle(self, gui):
        r = 0.5
        volume = 4.0 / 3.0 * np.pi * r**3
        expected = volume - 4.0 / 3.0 * np.pi * (r - 0.1) ** 3
        volumes = np.array([volume])
        result = gui.attainable_mass_simulate(volumes)
        assert_allclose(result[0], expected, atol=1e-15)

    def test_mixed_sizes(self, gui):
        r_tiny = 0.05
        r_large = 0.5
        v_tiny = 4.0 / 3.0 * np.pi * r_tiny**3
        v_large = 4.0 / 3.0 * np.pi * r_large**3
        volumes = np.array([v_tiny, v_large])
        result = gui.attainable_mass_simulate(volumes)
        assert_allclose(result[0], v_tiny, atol=1e-15)
        expected_large = v_large - 4.0 / 3.0 * np.pi * (r_large - 0.1) ** 3
        assert_allclose(result[1], expected_large, atol=1e-15)


class TestEySimulate:
    def test_unit_surface(self, gui):
        surfaces = np.array([1.0])
        result = gui.ey_simulate(surfaces)
        speed = 1.0
        expected = speed / (0.25014 + speed) * 0.3
        assert_allclose(result[0], expected, atol=1e-10)

    def test_large_surface(self, gui):
        surfaces = np.array([1e6])
        result = gui.ey_simulate(surfaces)
        assert result[0] < 0.001

    def test_small_surface(self, gui):
        surfaces = np.array([0.001])
        result = gui.ey_simulate(surfaces)
        assert_allclose(result[0], 0.3, atol=0.001)


class TestLighter:
    def test_zero_percent(self, gui):
        result = gui.lighter((0.5, 0.5, 0.5), 0.0)
        assert_allclose(result, (0.5, 0.5, 0.5), atol=1e-10)

    def test_100_percent(self, gui):
        result = gui.lighter((0.5, 0.5, 0.5), 1.0)
        assert_allclose(result, (1.0, 1.0, 1.0), atol=1e-10)

    def test_black_50_percent(self, gui):
        result = gui.lighter((0, 0, 0), 0.5)
        assert_allclose(result, (0.5, 0.5, 0.5), atol=1e-10)
