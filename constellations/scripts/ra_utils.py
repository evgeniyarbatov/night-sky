import numpy as np
from numpy.typing import ArrayLike


def ra_hms_to_deg(ra_hms: str) -> float:
    """Convert a "H M S" right-ascension string to decimal degrees."""
    h, m, s = (float(x) for x in ra_hms.strip().split())
    return (h + m / 60 + s / 3600) * 15


def circular_mean_deg(angles_deg: ArrayLike) -> float:
    """Mean of angles in degrees on a circle (handles 0°/360° wrap)."""
    rad = np.deg2rad(np.asarray(angles_deg, dtype=float))
    mean = float(np.rad2deg(np.atan2(np.mean(np.sin(rad)), np.mean(np.cos(rad)))))
    return mean % 360.0


def unwrap_degrees(angles_deg: ArrayLike) -> list[float]:
    """Unwrap a degree series so successive samples differ by at most 180°."""
    unwrapped = np.rad2deg(np.unwrap(np.deg2rad(np.asarray(angles_deg, dtype=float))))
    return [float(x) for x in unwrapped]
