import os

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
GOLDEN_CSV = os.path.join(FIXTURES_DIR, "golden_clusters.csv")


def _create_synthetic_psd_image():
    """50x50 image with 3 dark circles at known positions."""
    from PIL import Image

    img = Image.new("RGB", (50, 50), (255, 255, 255))
    arr = np.array(img)
    circles = [(15, 15, 4), (35, 15, 3), (25, 35, 5)]
    for cx, cy, radius in circles:
        y_grid, x_grid = np.ogrid[:50, :50]
        mask = (x_grid - cx) ** 2 + (y_grid - cy) ** 2 <= radius**2
        arr[mask, 0] = 20
        arr[mask, 1] = 20
        arr[mask, 2] = 20
    return Image.fromarray(arr)


def _run_pipeline(gui):
    """Run threshold + launch_psd + refresh on synthetic image."""
    img = _create_synthetic_psd_image()
    gui.img_source = img
    gui.polygon_alpha = None
    gui.polygon_beta = None
    gui.threshold_var.set("58.8")
    gui.pixel_scale_var.set("10.0")
    gui.max_cluster_axis_var.set("100")
    gui.min_surface_var.set("3")
    gui.min_roundness_var.set("0")
    gui.maxcost_var.set("0.35")
    gui.last_image_x = 500
    gui.last_image_y = 500

    gui.threshold_image(None)
    assert gui.mask_threshold is not None

    gui.launch_psd(None)

    return {
        "SURFACE": gui.clusters_surface.copy(),
        "LONG_AXIS": gui.clusters_long_axis.copy(),
        "SHORT_AXIS": gui.clusters_short_axis.copy(),
        "ROUNDNESS": gui.clusters_roundness.copy(),
        "VOLUME": gui.clusters_volume.copy(),
    }


class TestGoldenFileSnapshot:
    @pytest.fixture(autouse=True)
    def setup(self, gui):
        self.gui = gui

    def test_generate_golden_file(self):
        """Generate golden snapshot if it doesn't exist yet."""
        data = _run_pipeline(self.gui)

        if not os.path.exists(GOLDEN_CSV):
            os.makedirs(FIXTURES_DIR, exist_ok=True)
            df = pd.DataFrame(data)
            df.to_csv(GOLDEN_CSV, index=False)
            pytest.skip("Golden file created — re-run to validate")

        df_golden = pd.read_csv(GOLDEN_CSV)
        assert len(data["SURFACE"]) == len(df_golden), (
            f"Particle count changed: {len(data['SURFACE'])} vs golden {len(df_golden)}"
        )
        assert_allclose(
            data["SURFACE"],
            df_golden["SURFACE"].values,
            atol=1e-10,
            err_msg="SURFACE values diverged from golden file",
        )
        assert_allclose(
            data["LONG_AXIS"],
            df_golden["LONG_AXIS"].values,
            atol=1e-10,
            err_msg="LONG_AXIS values diverged from golden file",
        )
        assert_allclose(
            data["SHORT_AXIS"],
            df_golden["SHORT_AXIS"].values,
            atol=1e-10,
            err_msg="SHORT_AXIS values diverged from golden file",
        )
        assert_allclose(
            data["ROUNDNESS"],
            df_golden["ROUNDNESS"].values,
            atol=1e-10,
            err_msg="ROUNDNESS values diverged from golden file",
        )
        assert_allclose(
            data["VOLUME"],
            df_golden["VOLUME"].values,
            atol=1e-10,
            err_msg="VOLUME values diverged from golden file",
        )
