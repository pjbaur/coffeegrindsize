import pytest
import numpy as np
from PIL import Image
from tkinter import Tk


@pytest.fixture(scope="session")
def tk_root():
    root = Tk()
    root.withdraw()
    yield root
    root.destroy()


@pytest.fixture()
def gui(tk_root):
    from coffeegrindsize import coffeegrindsize_GUI

    instance = coffeegrindsize_GUI(tk_root)
    yield instance
    instance.nclusters = None
    instance.cluster_data = None
    instance.mask_threshold = None


@pytest.fixture()
def synthetic_white_image():
    return Image.new("RGB", (100, 100), (255, 255, 255))


@pytest.fixture()
def synthetic_image_with_dark_circle():
    img = Image.new("RGB", (100, 100), (255, 255, 255))
    arr = np.array(img)
    cx, cy, radius = 50, 50, 10
    y_grid, x_grid = np.ogrid[:100, :100]
    mask = (x_grid - cx) ** 2 + (y_grid - cy) ** 2 <= radius**2
    arr[mask, 0] = 20
    arr[mask, 1] = 20
    arr[mask, 2] = 20
    return Image.fromarray(arr), (cx, cy), radius


@pytest.fixture()
def synthetic_two_circles_image():
    img = Image.new("RGB", (100, 100), (255, 255, 255))
    arr = np.array(img)
    for cx, cy, radius in [(25, 25, 5), (75, 75, 5)]:
        y_grid, x_grid = np.ogrid[:100, :100]
        mask = (x_grid - cx) ** 2 + (y_grid - cy) ** 2 <= radius**2
        arr[mask, 0] = 20
        arr[mask, 1] = 20
        arr[mask, 2] = 20
    return Image.fromarray(arr)


@pytest.fixture()
def sample_cluster_data():
    n = 10
    rng = np.random.RandomState(42)
    surfaces = rng.uniform(5, 50, n)
    long_axes = rng.uniform(2, 10, n)
    short_axes = rng.uniform(1, long_axes)
    roundness = short_axes / long_axes * rng.uniform(0.5, 1.0, n)
    volumes = (4.0 / 3.0) * np.pi * (long_axes / 2) ** 3
    return {
        "surfaces": surfaces,
        "long_axes": long_axes,
        "short_axes": short_axes,
        "roundness": roundness,
        "volumes": volumes,
        "pixel_scale": 10.0,
    }


@pytest.fixture()
def sample_csv_content():
    return (
        "ID,SURFACE,ROUNDNESS,SHORT_AXIS,LONG_AXIS,VOLUME,PIXEL_SCALE\n"
        "0,10.5,0.8,3.2,4.0,33.51,10.0\n"
        "1,20.3,0.7,4.1,5.8,81.05,10.0\n"
    )
