from scripts.utils import (
    VIEW_ANGLES,
    Point,
    add_view_angles,
    get_timezone_from_points,
    limit_points,
)


def test_get_timezone_from_points_empty():
    assert get_timezone_from_points([]) == "UTC"


def test_get_timezone_from_points_new_york():
    points = [
        Point(time="t1", timestamp="1", lat=40.7128, lon=-74.0060, az=0.0, alt=0.0),
        Point(time="t2", timestamp="2", lat=40.7306, lon=-73.9352, az=0.0, alt=0.0),
    ]

    assert get_timezone_from_points(points) == "America/New_York"


def test_add_view_angles_includes_overhead():
    point = Point(time="t1", timestamp="100", lat=1.0, lon=2.0, az=350.0, alt=0.0)
    views = add_view_angles([point])

    assert len(views) == len(VIEW_ANGLES)
    assert views[0].alt == 0.0
    assert 90.0 in [view.alt for view in views]

    assert [view.az for view in views] == [point.az] * len(VIEW_ANGLES)
    assert len({view.timestamp for view in views}) == len(views)


def test_limit_points_caps_and_spreads():
    points = [
        Point(time="t", timestamp=str(i), lat=0.0, lon=0.0, az=float(i), alt=0.0)
        for i in range(25)
    ]

    limited = limit_points(points, max_points=10)

    assert len(limited) == 10
    assert limited[0] == points[0]
    assert limited[-1] == points[-1]
