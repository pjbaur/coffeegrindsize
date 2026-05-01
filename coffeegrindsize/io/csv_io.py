"""CSV serialization helpers."""

import pandas as pd


def build_clusters_dataframe(clusters_surface, clusters_roundness, clusters_short_axis, clusters_long_axis, clusters_volume, pixel_scale):
    dataframe = pd.DataFrame(
        {
            "SURFACE": clusters_surface,
            "ROUNDNESS": clusters_roundness,
            "SHORT_AXIS": clusters_short_axis,
            "LONG_AXIS": clusters_long_axis,
            "VOLUME": clusters_volume,
            "PIXEL_SCALE": pixel_scale,
        }
    )
    dataframe.index.name = "ID"
    return dataframe


def load_clusters_dataframe(csv_data_filename):
    return pd.read_csv(csv_data_filename)


def build_stats_dataframe(avg_diam, std_diam, avg_surf, std_surf, eff, qual):
    return pd.DataFrame(
        {
            "AVG_DIAM": [avg_diam],
            "STD_DIAM": [std_diam],
            "AVG_SURF": [avg_surf],
            "STD_SURF": [std_surf],
            "EFF": [eff],
            "QUAL": [qual],
        }
    )
