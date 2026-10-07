from pathlib import Path

from scripts.profile import (
    build_route_profile,
    load_constellation_content,
    render_profile_markdown,
    seasonal_rotation,
    write_constellation_cards,
)

SAMPLE = Path("data/samples/sample_night_run.gpx")


def test_route_profile() -> None:
    profile = build_route_profile(str(SAMPLE), with_zoom=False)
    assert profile["run_id"] == "sample_night_run"
    assert profile["summary"]
    assert profile["light_pollution_note"]
    md = render_profile_markdown(profile)
    assert "Route sky profile" in md


def test_seasonal_rotation_has_twelve_months() -> None:
    season = seasonal_rotation(str(SAMPLE))
    assert len(season["months"]) == 12
    names = [m["month_name"] for m in season["months"]]
    assert "January" in names
    assert "July" in names
    # Highlights or constellations should vary across the year for a fixed pointing
    signatures = [
        (m.get("highlight"), tuple(m.get("constellations", [])[:2])) for m in season["months"]
    ]
    assert len(set(signatures)) >= 2


def test_constellation_cards(tmp_path: Path) -> None:
    profile = {
        "constellations": [
            {"name": "Orion", "count": 2},
            {"name": "Unknown Constellation", "count": 1},
        ]
    }
    content = load_constellation_content()
    assert "Orion" in content
    paths = write_constellation_cards(profile, tmp_path / "cards", content)
    assert len(paths) == 2
    orion = (tmp_path / "cards" / "orion.md").read_text()
    assert "Myth" in orion
    assert "Wonder" in orion
