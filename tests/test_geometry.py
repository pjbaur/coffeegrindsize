import numpy as np


class TestPointsAlongPolygon:
    def test_point_on_edge(self, gui):
        X_points = np.array([5.0])
        Y_points = np.array([0.0])
        X_polygon = np.array([0.0, 10.0])
        Y_polygon = np.array([0.0, 0.0])
        result = gui.points_along_polygon(X_points, Y_points, X_polygon, Y_polygon)
        assert result.size > 0

    def test_point_far(self, gui):
        X_points = np.array([5.0])
        Y_points = np.array([5.0])
        X_polygon = np.array([0.0, 10.0])
        Y_polygon = np.array([0.0, 0.0])
        result = gui.points_along_polygon(X_points, Y_points, X_polygon, Y_polygon)
        assert result.size == 0

    def test_empty_points(self, gui):
        X_points = np.array([])
        Y_points = np.array([])
        X_polygon = np.array([0.0, 10.0])
        Y_polygon = np.array([0.0, 0.0])
        result = gui.points_along_polygon(X_points, Y_points, X_polygon, Y_polygon)
        assert result.size == 0

    def test_multiple_points_on_segment(self, gui):
        X_points = np.array([2.0, 5.0, 8.0])
        Y_points = np.array([0.0, 0.0, 0.0])
        X_polygon = np.array([0.0, 10.0])
        Y_polygon = np.array([0.0, 0.0])
        result = gui.points_along_polygon(X_points, Y_points, X_polygon, Y_polygon)
        assert set(result) == {0, 1, 2}
