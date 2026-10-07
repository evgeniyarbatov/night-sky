from scripts.gpx import SAMPLE_GPX
from scripts.utils import load_points


def test_sample_gpx_exists() -> None:
    assert SAMPLE_GPX.is_file()


def test_load_points_from_sample() -> None:
    points = load_points(str(SAMPLE_GPX), with_zoom=False)
    assert len(points) >= 1
    assert all(p.fov > 0 for p in points)
    # View angles include horizon
    assert any(p.alt == 0.0 for p in points)
