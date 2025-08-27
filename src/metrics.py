import numpy as np


def team_centroid(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    return float(np.nanmean(x)), float(np.nanmean(y))


def team_length(x, y):
    """Length ~ distance between back-most and front-most players (y-range)."""
    y = np.array(y, dtype=float)
    return float(np.nanmax(y) - np.nanmin(y))


def team_width(x, y):
    """Width ~ lateral spread (x-range)."""
    x = np.array(x, dtype=float)
    return float(np.nanmax(x) - np.nanmin(x))
