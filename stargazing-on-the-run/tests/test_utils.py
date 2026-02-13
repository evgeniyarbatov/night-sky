from scripts.utils import VIEW_ANGLES, Point, add_view_angles, get_timezone_from_points


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
    views = add_view_angles([point, point])

    assert [view.alt for view in views].count(0.0) == 2

    extra_alts = [alt for alt in VIEW_ANGLES if alt != 0]
    for alt in extra_alts:
        assert [view.alt for view in views].count(alt) == 1


def test_add_view_angles_reuses_points_when_needed():
    point = Point(time="t1", timestamp="100", lat=1.0, lon=2.0, az=350.0, alt=0.0)
    views = add_view_angles([point])

    assert [view.alt for view in views].count(0.0) == 1
    extra_alts = [alt for alt in VIEW_ANGLES if alt != 0]
    for alt in extra_alts:
        assert [view.alt for view in views].count(alt) == 1
