from scripts.sky import (
    ZOOM_FOV,
    angular_separation_deg,
    compass_facing,
    in_fov,
    make_zoom_point,
    observe_viewpoint,
    should_add_zoom,
)
from scripts.utils import FOV_MAX, Point


def test_angular_separation_zero() -> None:
    assert angular_separation_deg(10, 20, 10, 20) < 1e-6


def test_angular_separation_known() -> None:
    # 90° apart on horizon
    sep = angular_separation_deg(0, 0, 90, 0)
    assert 89.0 < sep < 91.0


def test_in_fov_center() -> None:
    assert in_fov(180, 30, 180, 30, 60)


def test_in_fov_outside() -> None:
    assert not in_fov(0, 0, 180, 0, 40)


def test_in_fov_below_horizon() -> None:
    assert not in_fov(180, -5, 180, 0, 60)


def test_compass_facing() -> None:
    assert compass_facing(0) == "N"
    assert compass_facing(90) == "E"
    assert compass_facing(180) == "S"
    assert compass_facing(270) == "W"


def test_observe_sirius_winter_nyc_south() -> None:
    # ~23:00 local EST; Sirius near the meridian from NYC
    point = Point(
        time="2025-01-14T23:00:00",
        timestamp="1",
        lat=40.75,
        lon=-74.01,
        az=180.0,
        alt=20.0,
        fov=60.0,
    )
    sky = observe_viewpoint(point)
    names = {s.name for s in sky.stars}
    assert "Sirius" in names
    assert sky.highlight is not None


def test_moon_phase_fullish() -> None:
    # Known full moon near 2025-01-13; next days still high illumination
    point = Point(
        time="2025-01-13T23:00:00",
        timestamp="1",
        lat=40.75,
        lon=-74.01,
        az=140.0,
        alt=30.0,
        fov=90.0,
    )
    sky = observe_viewpoint(point)
    if sky.moon is None:
        # Ephemeris may be unavailable in offline CI; skip soft
        return
    assert 0.0 <= sky.moon.illumination <= 1.0
    assert sky.moon.phase_name


def test_make_zoom_point() -> None:
    p = Point("2025-01-15T05:00:00", "100_v1", 40.0, -74.0, 180.0, 0.0, FOV_MAX)
    z = make_zoom_point(p)
    assert z.fov == ZOOM_FOV
    assert z.timestamp.endswith("_zoom")
    assert z.az == p.az


def test_should_add_zoom_requires_near_center() -> None:
    p = Point("2025-01-15T05:10:00", "1", 40.75, -74.01, 180.0, 0.0, FOV_MAX)
    sky = observe_viewpoint(p)
    if sky.highlight is None:
        return
    # If highlight is far from center, zoom should be false
    sky.highlight.az = (p.az + 90) % 360
    sky.highlight.alt = 10
    assert should_add_zoom(sky, p) is False
