from datetime import datetime
from pathlib import Path

from scripts.tonight import (
    build_tonight,
    render_audio_script,
    render_glance_card,
    select_highlights,
    shift_points_to_start,
)
from scripts.utils import load_points

SAMPLE = Path("data/samples/sample_night_run.gpx")


def test_shift_points_to_start() -> None:
    points = load_points(str(SAMPLE), with_zoom=False)
    start = datetime(2026, 7, 24, 21, 30, 0)
    shifted = shift_points_to_start(points, start)
    assert len(shifted) == len(points)
    first = datetime.strptime(shifted[0].time, "%Y-%m-%dT%H:%M:%S")
    # First viewpoint local time equals planned start (same clock offset as original span)
    times = [datetime.strptime(p.time, "%Y-%m-%dT%H:%M:%S") for p in points]
    t0 = min(times)
    expected0 = start + (times[0] - t0)
    assert first == expected0


def test_select_highlights_caps_and_unique() -> None:
    viewpoints = [
        {
            "minute_into_run": 0,
            "sky": {"highlight": {"name": "Sirius", "magnitude": -1.4, "alt": 30}},
        },
        {
            "minute_into_run": 5,
            "sky": {"highlight": {"name": "Sirius", "magnitude": -1.4, "alt": 32}},
        },
        {
            "minute_into_run": 10,
            "sky": {"highlight": {"name": "Vega", "magnitude": 0.0, "alt": 40}},
        },
        {
            "minute_into_run": 15,
            "sky": {"highlight": {"name": "Mars", "magnitude": 0.5, "alt": 20}},
        },
        {
            "minute_into_run": 20,
            "sky": {"highlight": {"name": "Polaris", "magnitude": 2.0, "alt": 40}},
        },
    ]
    chosen = select_highlights(viewpoints, limit=3)
    assert len(chosen) <= 3
    names = [c["sky"]["highlight"]["name"] for c in chosen]
    assert len(names) == len(set(names))
    assert chosen == sorted(chosen, key=lambda v: v["minute_into_run"])


def test_build_tonight_offline() -> None:
    start = datetime(2025, 1, 15, 21, 0, 0)
    preview = build_tonight(str(SAMPLE), start, weather=False)
    assert preview["start"].startswith("2025-01-15")
    assert "highlights" in preview
    assert "moon" in preview
    md = render_glance_card(preview)
    assert "glance" in md.lower() or "Tonight" in md
    script = render_audio_script(preview)
    assert "tonight" in script.lower() or "Look" in script or "Highlight" in script


def test_weather_mocked() -> None:
    def fake_weather(lat: float, lon: float, start: datetime, end: datetime) -> dict[str, object]:
        return {
            "summary": "Mostly clear (avg cloud cover ~10%).",
            "hourly": [],
            "avg_cloud_cover": 10,
        }

    start = datetime(2025, 1, 15, 21, 0, 0)
    preview = build_tonight(str(SAMPLE), start, weather=True, weather_fetcher=fake_weather)
    assert preview["weather"]["avg_cloud_cover"] == 10
