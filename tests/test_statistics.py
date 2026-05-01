

class TestUpdateStatistics:
    def test_basic_statistics(self, gui, sample_cluster_data):
        d = sample_cluster_data
        gui.nclusters = 10
        gui.clusters_surface = d["surfaces"]
        gui.clusters_long_axis = d["long_axes"]
        gui.clusters_short_axis = d["short_axes"]
        gui.clusters_volume = d["volumes"]
        gui.pixel_scale_var.set(str(d["pixel_scale"]))

        gui.update_statistics()

        diam_avg = gui.diam_average_var.get()
        diam_std = gui.diam_stddev_var.get()
        surf_avg = gui.surf_average_var.get()
        surf_std = gui.surf_stddev_var.get()
        eff = gui.eff_var.get()
        q = gui.q_var.get()

        assert float(diam_avg) > 0
        assert float(diam_std) > 0
        assert float(surf_avg) > 0
        assert float(surf_std) > 0
        assert float(eff) > 0
        assert float(q) > 0

    def test_no_clusters_returns(self, gui):
        gui.nclusters = None
        gui.update_statistics()
        assert gui.diam_average_var.get() == "None"

    def test_invalid_pixel_scale_returns(self, gui, sample_cluster_data):
        d = sample_cluster_data
        gui.nclusters = 10
        gui.clusters_surface = d["surfaces"]
        gui.clusters_long_axis = d["long_axes"]
        gui.clusters_short_axis = d["short_axes"]
        gui.clusters_volume = d["volumes"]
        gui.pixel_scale_var.set("not_a_number")
        gui.update_statistics()
        assert gui.diam_average_var.get() == "None"
