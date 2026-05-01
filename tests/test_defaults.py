import pytest


class TestModuleConstants:
    def test_reference_objects_dict(self):
        from coffeegrindsize import reference_objects_dict

        assert len(reference_objects_dict) == 14
        assert reference_objects_dict["US Quarter"] == 24.26
        assert reference_objects_dict["Custom"] is None

    def test_comparison_class(self):
        from coffeegrindsize import Comparison

        c = Comparison(a=1, b="hello")
        assert c.a == 1
        assert c.b == "hello"

    def test_default_constants(self):
        from coffeegrindsize import (
            def_threshold,
            def_maxcost,
            def_min_surface,
            def_max_cluster_axis,
            def_min_roundness,
            coffee_cell_size,
            default_log_binsize,
            default_binsize,
        )

        assert def_threshold == 58.8
        assert def_maxcost == 0.35
        assert def_min_surface == 5
        assert def_max_cluster_axis == 100
        assert def_min_roundness == 0
        assert coffee_cell_size == 20.0
        assert default_log_binsize == 0.05
        assert default_binsize == 0.1

    def test_display_names(self):
        from coffeegrindsize import (
            original_image_display_name,
            threshold_image_display_name,
            outlines_image_display_name,
            histogram_image_display_name,
        )

        assert original_image_display_name == "Original"
        assert threshold_image_display_name == "Thresholded"
        assert outlines_image_display_name == "Cluster Outlines"
        assert histogram_image_display_name == "Histograms"
