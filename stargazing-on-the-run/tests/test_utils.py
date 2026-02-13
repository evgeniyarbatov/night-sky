from scripts.utils import Point, get_timezone_from_points


def test_get_timezone_from_points_empty():
    assert get_timezone_from_points([]) == "UTC"


def test_get_timezone_from_points_new_york():
    points = [
        Point(time="t1", timestamp="1", lat=40.7128, lon=-74.0060, az=0.0),
        Point(time="t2", timestamp="2", lat=40.7306, lon=-73.9352, az=0.0),
    ]

    assert get_timezone_from_points(points) == "America/New_York"
