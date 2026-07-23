def ra_hms_to_deg(ra_hms: str) -> float:
    """Convert a "H M S" right-ascension string to decimal degrees."""
    h, m, s = (float(x) for x in ra_hms.strip().split())
    return (h + m / 60 + s / 3600) * 15
