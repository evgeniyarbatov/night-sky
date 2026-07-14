import datetime as dt

import pytest

import planets


def test_load_settings_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CITY_NAME", "Hanoi")
    monkeypatch.setenv("COUNTRY", "Vietnam")
    monkeypatch.setenv("LATITUDE", "20.5")
    monkeypatch.setenv("LONGITUDE", "105.2")
    monkeypatch.setenv("TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("SAMPLE_INTERVAL_MINUTES", "15")
    monkeypatch.setenv("ELEVATION_M", "12.3")

    settings = planets.load_settings(load_dotenv_file=False)

    assert settings.city_name == "Hanoi"
    assert settings.country == "Vietnam"
    assert settings.latitude == 20.5
    assert settings.longitude == 105.2
    assert settings.timezone_str == "Asia/Ho_Chi_Minh"
    assert settings.sample_interval_minutes == 15
    assert settings.elevation_m == 12.3


def test_load_settings_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CITY_NAME", raising=False)
    monkeypatch.setenv("COUNTRY", "Vietnam")
    monkeypatch.setenv("LATITUDE", "20.5")
    monkeypatch.setenv("LONGITUDE", "105.2")
    monkeypatch.setenv("TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("SAMPLE_INTERVAL_MINUTES", "15")
    monkeypatch.setenv("ELEVATION_M", "12.3")

    with pytest.raises(ValueError, match="Missing required setting: CITY_NAME"):
        planets.load_settings(load_dotenv_file=False)


def test_load_settings_invalid_interval(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CITY_NAME", "Hanoi")
    monkeypatch.setenv("COUNTRY", "Vietnam")
    monkeypatch.setenv("LATITUDE", "20.5")
    monkeypatch.setenv("LONGITUDE", "105.2")
    monkeypatch.setenv("TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("SAMPLE_INTERVAL_MINUTES", "0")
    monkeypatch.setenv("ELEVATION_M", "12.3")

    with pytest.raises(ValueError, match="SAMPLE_INTERVAL_MINUTES must be positive"):
        planets.load_settings(load_dotenv_file=False)


def test_load_settings_missing_country(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CITY_NAME", "Hanoi")
    monkeypatch.delenv("COUNTRY", raising=False)
    monkeypatch.setenv("LATITUDE", "20.5")
    monkeypatch.setenv("LONGITUDE", "105.2")
    monkeypatch.setenv("TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("SAMPLE_INTERVAL_MINUTES", "15")
    monkeypatch.setenv("ELEVATION_M", "12.3")

    with pytest.raises(ValueError, match="Missing required setting: COUNTRY"):
        planets.load_settings(load_dotenv_file=False)


def test_get_wall_distance_for_azimuth_wrap() -> None:
    wall_distances: dict[int, float] = {0: 100.0, 90: 200.0, 270: 300.0}
    distance, direction = planets.get_wall_distance_for_azimuth(350, wall_distances)

    assert direction == 0
    assert distance == 100


def test_get_cardinal_direction_boundaries() -> None:
    assert planets.get_cardinal_direction(0) == "North"
    assert planets.get_cardinal_direction(22.5) == "NNE"
    assert planets.get_cardinal_direction(45) == "NE"
    assert planets.get_cardinal_direction(359) == "NNW"
    assert planets.get_cardinal_direction(360) == "North"


def _visibility_summary(avg_az: float) -> planets.VisibilitySummary:
    return {
        "planet": "Test",
        "visible": True,
        "avg_alt": 10.0,
        "avg_az": avg_az,
        "rise_time": None,
        "set_time": None,
    }


def test_group_visible_planets_by_azimuth() -> None:
    visible_planets = [
        _visibility_summary(7),
        _visibility_summary(14),
        _visibility_summary(359),
        _visibility_summary(360),
        _visibility_summary(181),
    ]

    groups = planets.group_visible_planets_by_azimuth(visible_planets)

    assert sorted(groups.keys()) == [0, 15, 180]
    assert len(groups[0]) == 3
    assert len(groups[15]) == 1
    assert len(groups[180]) == 1


def test_summarize_visibility_visible_case() -> None:
    times = [
        dt.datetime(2024, 1, 1, 18, 0),
        dt.datetime(2024, 1, 1, 19, 0),
        dt.datetime(2024, 1, 1, 20, 0),
    ]
    altitudes = [-2.0, 10.0, 20.0]
    azimuths = [90.0, 100.0, 110.0]

    summary = planets.summarize_visibility("Mars", altitudes, azimuths, times)

    assert summary["visible"] is True
    assert summary["avg_alt"] == pytest.approx(15.0)
    assert summary["avg_az"] == pytest.approx(105.0)
    assert summary["rise_time"] == times[1]
    assert summary["set_time"] == times[2]


def test_summarize_visibility_not_visible() -> None:
    times = [
        dt.datetime(2024, 1, 1, 18, 0),
        dt.datetime(2024, 1, 1, 19, 0),
    ]
    altitudes = [-1.0, 0.0]
    azimuths = [100.0, 110.0]

    summary = planets.summarize_visibility("Venus", altitudes, azimuths, times)

    assert summary["visible"] is False
    assert summary["avg_alt"] is None
    assert summary["avg_az"] is None
    assert summary["rise_time"] is None
    assert summary["set_time"] is None


def test_compute_wall_projection_height() -> None:
    height = planets.compute_wall_projection_height(45.0, 100.0)

    assert height == pytest.approx(100.0)
