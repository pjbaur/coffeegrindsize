"""Statistical calculations for particle data."""

from dataclasses import dataclass

import numpy as np

from coffeegrindsize.analysis.simulation import attainable_mass_simulate
from coffeegrindsize.config import coffee_cell_size


@dataclass(frozen=True)
class ParticleStatistics:
    diameters_average: float
    diameters_stddev: float
    surfaces_average: float
    surfaces_stddev: float
    effs_average: float
    quality: float


def weighted_stddev(data, weights, frequency=False, unbiased=True):
    if unbiased is True:
        if frequency is True:
            bias_estimator = (np.nansum(weights) - 1.0) / np.nansum(weights)
        else:
            bias_estimator = 1.0 - (np.nansum(weights**2)) / (np.nansum(weights) ** 2)
    else:
        bias_estimator = 1.0

    weights = weights / np.nansum(weights)
    wmean = np.nansum(data * weights)
    deviations = data - wmean
    wvar = np.nansum(deviations**2 * weights) / bias_estimator
    return np.sqrt(wvar)


def compute_particle_statistics(clusters_long_axis, clusters_short_axis, clusters_surface, clusters_volume, pixel_scale):
    diameters = 2 * np.sqrt(clusters_long_axis * clusters_short_axis) / pixel_scale
    surfaces = clusters_surface / pixel_scale**2
    volumes = clusters_volume / pixel_scale**3
    attainable_masses = attainable_mass_simulate(volumes)
    effs = attainable_masses / volumes

    weights = np.maximum(np.ceil(attainable_masses / (coffee_cell_size / 1e3) ** 3), 1)
    diameters_average = np.sum(diameters * weights) / np.sum(weights)
    diameters_stddev = weighted_stddev(diameters, weights, frequency=True, unbiased=True)

    weights = np.maximum(np.ceil(attainable_masses / (coffee_cell_size / 1e3) ** 3), 1)
    surfaces_average = np.sum(surfaces * weights) / np.sum(weights)
    surfaces_stddev = weighted_stddev(surfaces, weights, frequency=True, unbiased=True)
    quality = surfaces_average / surfaces_stddev

    effs_average = np.mean(effs) * 100

    return ParticleStatistics(
        diameters_average=diameters_average,
        diameters_stddev=diameters_stddev,
        surfaces_average=surfaces_average,
        surfaces_stddev=surfaces_stddev,
        effs_average=effs_average,
        quality=quality,
    )
