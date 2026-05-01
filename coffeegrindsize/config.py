"""Configuration constants for Coffee Grind Size Analyzer."""

import os
import time

def_display_advanced_options = False
def_expert_mode = False

# Threshold to select reference dark pixel.
def_reference_threshold = 0.4
nsmooth = 3

def_maxcost = 0.35
def_threshold = 58.8
def_pixel_scale = None
def_max_cluster_axis = 100
def_min_surface = 5
def_min_roundness = 0

def_min_x_axis = 0.01
def_max_x_axis = 10

coffee_cell_size = 20.0
def_session_name = "PSD_" + time.strftime("%Y%m%d_%Hh%Mm%Ss")

original_image_display_name = "Original"
threshold_image_display_name = "Thresholded"
outlines_image_display_name = "Cluster Outlines"
histogram_image_display_name = "Histograms"

default_log_binsize = 0.05
default_binsize = 0.1

reference_objects_dict = {
    "Custom": None,
    "Canadian Quarter": 23.81,
    "Canadian Dollar": 26.5,
    "Canadian Dime": 18.03,
    "Canadian Two Dollars": 28.0,
    "Canadian Five Cents": 21.3,
    "US Quarter": 24.26,
    "US Dollar": 26.92,
    "US Dime": 17.91,
    "US Penny": 19.05,
    "2 Euros": 25.75,
    "1 Euro": 23.25,
    "50 Euro Cents": 24.25,
    "20 Euro Cents": 22.25,
}

def_output_dir = os.path.expanduser("~")
