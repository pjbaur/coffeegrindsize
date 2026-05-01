"""Particle extraction simulations."""

from typing import Any

import numpy as np
from numpy.typing import NDArray


def attainable_mass_simulate(volumes: NDArray[np.number[Any]]) -> NDArray[np.floating[Any]]:
    """Estimate reachable volume after accounting for an inaccessible core."""
    depth_limit = 0.1  # mm

    radii = (3.0 / 4.0 * volumes / np.pi) ** (1 / 3)
    unreachable_volumes = np.full(volumes.size, 0.0)

    iboulders = np.where(radii > depth_limit)
    unreachable_volumes[iboulders[0]] = 4.0 / 3.0 * np.pi * (radii[iboulders[0]] - depth_limit) ** 3
    return volumes - unreachable_volumes


def ey_simulate(surfaces: NDArray[np.number[Any]]) -> NDArray[np.floating[Any]]:
    """Estimate extraction yield from particle surfaces."""
    k_reference = 0.25014
    extraction_limit = 0.3
    extraction_speed = 1.0 / surfaces
    return extraction_speed / (k_reference + extraction_speed) * extraction_limit
