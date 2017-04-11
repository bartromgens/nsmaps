#!/usr/bin/env python3

import sys
import os

import numpy

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)

import nsmaps
from nsmaps.logger import logger


DATA_DIR = './data/'


def create_merged_contour():
    min_level = 55
    max_level = 180
    n_levels = 37
    # n_levels = 100
    levels_minor = numpy.linspace(min_level, max_level, num=n_levels)
    config = nsmaps.contourmap.ContourPlotConfig()
    contourmap = nsmaps.contourmap.ContourMerged(config)
    contourmap.merge_grid_data(DATA_DIR)
    contourmap.create_geojson('combined.geojson', stroke_width=4, levels=levels_minor)


if __name__ == "__main__":
    create_merged_contour()