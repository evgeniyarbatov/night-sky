import pytest

import planets


def test_load_settings_success(monkeypatch):
    monkeypatch.setenv("CITY_NAME", "Hanoi")
    monkeypatch.setenv("LATITUDE", "20.5")
    monkeypatch.setenv("LONGITUDE", "105.2")
    monkeypatch.setenv("TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("SAMPLE_INTERVAL_MINUTES", "15")
    monkeypatch.setenv("ELEVATION_M", "12.3")

    settings = planets.load_settings(load_dotenv_file=False)

    assert settings.city_name == "Hanoi"
    assert settings.latitude == 20.5
    assert settings.longitude == 105.2
    assert settings.timezone_str == "Asia/Ho_Chi_Minh"
    assert settings.sample_interval_minutes == 15
    assert settings.elevation_m == 12.3


def test_load_settings_missing(monkeypatch):
    monkeypatch.delenv("CITY_NAME", raising=False)
    monkeypatch.setenv("LATITUDE", "20.5")
    monkeypatch.setenv("LONGITUDE", "105.2")
    monkeypatch.setenv("TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("SAMPLE_INTERVAL_MINUTES", "15")
    monkeypatch.setenv("ELEVATION_M", "12.3")

    with pytest.raises(ValueError, match="Missing required setting: CITY_NAME"):
        planets.load_settings(load_dotenv_file=False)


def test_load_settings_invalid_interval(monkeypatch):
    monkeypatch.setenv("CITY_NAME", "Hanoi")
    monkeypatch.setenv("LATITUDE", "20.5")
    monkeypatch.setenv("LONGITUDE", "105.2")
    monkeypatch.setenv("TIMEZONE", "Asia/Ho_Chi_Minh")
    monkeypatch.setenv("SAMPLE_INTERVAL_MINUTES", "0")
    monkeypatch.setenv("ELEVATION_M", "12.3")

    with pytest.raises(ValueError, match="SAMPLE_INTERVAL_MINUTES must be positive"):
        planets.load_settings(load_dotenv_file=False)


def test_get_wall_distance_for_azimuth_wrap():
    wall_distances = {0: 100, 90: 200, 270: 300}
    distance, direction = planets.get_wall_distance_for_azimuth(350, wall_distances)

    assert direction == 0
    assert distance == 100


def test_get_cardinal_direction_boundaries():
    assert planets.get_cardinal_direction(0) == "North"
    assert planets.get_cardinal_direction(22.5) == "NNE"
    assert planets.get_cardinal_direction(45) == "NE"
    assert planets.get_cardinal_direction(359) == "NNW"


def test_group_visible_planets_by_azimuth():
    visible_planets = [
        {"avg_az": 7},
        {"avg_az": 14},
        {"avg_az": 359},
        {"avg_az": 181},
    ]

    groups = planets.group_visible_planets_by_azimuth(visible_planets)

    assert sorted(groups.keys()) == [0, 15, 180]
    assert len(groups[0]) == 2
    assert len(groups[15]) == 1
    assert len(groups[180]) == 1
