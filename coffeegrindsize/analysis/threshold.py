"""Image thresholding core logic."""

import numpy as np
from matplotlib import path
from PIL import Image

from coffeegrindsize.analysis.geometry import points_along_polygon


def threshold_image_data(img_source, threshold, polygon_alpha=None, polygon_beta=None):
    """Return thresholding results without touching GUI state."""
    imdata_3d = np.array(img_source)
    imdata = imdata_3d[:, :, 2]
    mask_threshold_edge = None

    if polygon_alpha is not None:
        coord_list = [(polygon_alpha[0], polygon_beta[0])]
        npoly = polygon_alpha.size
        for i in range(npoly - 1):
            coord_list.append((polygon_alpha[i + 1], polygon_beta[i + 1]))
        poly = path.Path(coord_list)

        image_nx = imdata.shape[0]
        image_ny = imdata.shape[1]
        image_x = np.tile(np.arange(image_nx), (image_ny, 1)).T
        image_y = np.tile(np.arange(image_ny), (image_nx, 1))
        pts = np.vstack((image_y.flatten(), image_x.flatten())).T
        contained = poly.contains_points(pts)

        if not np.any(contained):
            return {
                "error": "No Image Pixels were Located Inside of the Analysis Region",
                "imdata": imdata,
                "background_median": None,
                "mask_threshold": None,
                "mask_threshold_edge": None,
                "img_threshold": None,
            }

        background_median = np.median(imdata.flatten()[np.where(contained)])
    else:
        poly = None
        background_median = np.median(imdata)

    mask_threshold = np.where(imdata < background_median * threshold / 100)

    if polygon_alpha is not None:
        pts = np.vstack((mask_threshold[1], mask_threshold[0])).T
        contained = poly.contains_points(pts)

        if not np.any(contained):
            return {
                "error": "No Thresholded Pixels were Located Inside of the Analysis Region",
                "imdata": imdata,
                "background_median": background_median,
                "mask_threshold": mask_threshold,
                "mask_threshold_edge": None,
                "img_threshold": None,
            }

        mask_threshold = (mask_threshold[0][np.where(contained)[0]], mask_threshold[1][np.where(contained)[0]])
        mask_threshold_edge = points_along_polygon(
            mask_threshold[1].astype(float),
            mask_threshold[0].astype(float),
            polygon_alpha,
            polygon_beta,
        )

    threshold_im_display = np.copy(imdata_3d)
    threshold_im_display[:, :, 0][mask_threshold] = 255
    threshold_im_display[:, :, 1][mask_threshold] = 0
    threshold_im_display[:, :, 2][mask_threshold] = 0

    return {
        "error": None,
        "imdata": imdata,
        "background_median": background_median,
        "mask_threshold": mask_threshold,
        "mask_threshold_edge": mask_threshold_edge,
        "img_threshold": Image.fromarray(threshold_im_display),
    }
