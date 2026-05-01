import numpy as np
from PIL import Image


class TestThresholdImage:
    def test_all_white_no_threshold(self, gui, synthetic_white_image):
        gui.img_source = synthetic_white_image
        gui.polygon_alpha = None
        gui.polygon_beta = None
        gui.threshold_var.set("58.8")
        gui.last_image_x = 500
        gui.last_image_y = 500
        gui.threshold_image(None)
        assert gui.mask_threshold is not None
        assert gui.mask_threshold[0].size == 0

    def test_half_dark_image(self, gui):
        arr = np.full((100, 100, 3), 255, dtype=np.uint8)
        arr[:50, :, 2] = 50
        img = Image.fromarray(arr)
        gui.img_source = img
        gui.polygon_alpha = None
        gui.polygon_beta = None
        gui.threshold_var.set("58.8")
        gui.last_image_x = 500
        gui.last_image_y = 500
        gui.threshold_image(None)
        assert gui.mask_threshold[0].size > 0
        fraction = gui.mask_threshold[0].size / (100 * 100)
        assert fraction > 0.3

    def test_no_image_returns_early(self, gui):
        gui.img_source = None
        result = gui.threshold_image(None)
        assert result is None
        assert gui.mask_threshold is None

    def test_invalid_threshold_returns_early(self, gui, synthetic_white_image):
        gui.img_source = synthetic_white_image
        gui.threshold_var.set("not_a_number")
        gui.threshold_image(None)
        assert gui.mask_threshold is None
