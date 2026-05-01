import os
import tempfile

import pandas as pd
from numpy.testing import assert_allclose


class TestSaveLoadRoundTrip:
    def test_save_and_read_csv(self, gui, sample_cluster_data):
        d = sample_cluster_data
        gui.nclusters = 10
        gui.clusters_surface = d["surfaces"]
        gui.clusters_roundness = d["roundness"]
        gui.clusters_long_axis = d["long_axes"]
        gui.clusters_short_axis = d["short_axes"]
        gui.clusters_volume = d["volumes"]
        gui.pixel_scale_var.set(str(d["pixel_scale"]))
        gui.expert_mode = True

        gui.update_statistics()

        with tempfile.TemporaryDirectory() as tmpdir:
            gui.output_dir = tmpdir
            gui.session_name_var.set("test_session")
            gui.save_data(None)

            csv_path = os.path.join(
                tmpdir, "test_session_data.csv"
            )
            assert os.path.exists(csv_path)

            df = pd.read_csv(csv_path)
            assert_allclose(
                df["SURFACE"].values, d["surfaces"], atol=1e-10
            )
            assert_allclose(
                df["LONG_AXIS"].values, d["long_axes"], atol=1e-10
            )
            assert_allclose(
                df["SHORT_AXIS"].values, d["short_axes"], atol=1e-10
            )
            assert_allclose(
                df["VOLUME"].values, d["volumes"], atol=1e-10
            )
            assert df["PIXEL_SCALE"].iloc[0] == d["pixel_scale"]

    def test_load_csv(self, gui, sample_csv_content, tmp_path):
        csv_file = tmp_path / "test_data.csv"
        csv_file.write_text(sample_csv_content)

        from unittest.mock import MagicMock, patch

        gui.create_histogram = MagicMock()

        with patch(
            "coffeegrindsize.filedialog.askopenfilename",
            return_value=str(csv_file),
        ):
            gui.output_dir = str(tmp_path)
            gui.load_data(None)

        assert gui.nclusters == 2
        assert gui.clusters_surface[0] == 10.5
        assert gui.pixel_scale_var.get() == "10.0"

    def test_save_no_clusters_returns(self, gui):
        gui.nclusters = None
        gui.save_data(None)
        # Should return early without error


class TestLoadComparisonData:
    def test_load_comparison(self, gui, sample_csv_content, tmp_path):
        csv_file = tmp_path / "comparison_data.csv"
        csv_file.write_text(sample_csv_content)

        from unittest.mock import MagicMock, patch

        gui.comparison_data_label_id = MagicMock()
        gui.simple_comparison_data_label_id = MagicMock()
        gui.img_histogram = None

        with patch(
            "coffeegrindsize.filedialog.askopenfilename",
            return_value=str(csv_file),
        ):
            gui.output_dir = str(tmp_path)
            gui.load_comparison_data(None)

        assert gui.comparison.nclusters == 2
        assert gui.comparison.clusters_surface[0] == 10.5
