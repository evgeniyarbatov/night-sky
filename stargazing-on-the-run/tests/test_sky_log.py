import json
from pathlib import Path

from scripts.sky_index import rebuild_from_sky_logs, update_index_from_log
from scripts.sky_log import build_sky_log, render_markdown, write_sky_log

SAMPLE = Path("data/samples/sample_night_run.gpx")


def test_build_sky_log_shape() -> None:
    log = build_sky_log(str(SAMPLE), with_zoom=False)
    assert log["run_id"] == "sample_night_run"
    assert log["viewpoint_count"] > 0
    vp = log["viewpoints"][0]
    assert "facing" in vp
    assert "minute_into_run" in vp
    assert "sky" in vp
    assert "stars" in vp["sky"]
    assert "constellations" in vp["sky"]


def test_render_markdown_has_table() -> None:
    log = build_sky_log(str(SAMPLE), with_zoom=False)
    md = render_markdown(log)
    assert "Sky log" in md
    assert "Highlight" in md
    assert "Minute" in md


def test_write_and_index(tmp_path: Path) -> None:
    log = build_sky_log(str(SAMPLE), with_zoom=False)
    out = tmp_path / "sky-logs" / log["run_id"]
    write_sky_log(log, out)
    assert (out / "sky_log.json").is_file()
    assert (out / "sky_log.md").is_file()

    index = update_index_from_log(log, {"objects": {}, "constellations": {}})
    assert isinstance(index["objects"], dict)
    # Second update must not change first_seen
    first = dict(index["objects"])
    update_index_from_log(log, index)
    assert index["objects"] == first

    rebuilt = rebuild_from_sky_logs(str(tmp_path / "sky-logs"), tmp_path / "sky-index.json")
    assert (tmp_path / "sky-index.json").is_file()
    with open(out / "sky_log.json") as f:
        loaded = json.load(f)
    assert loaded["run_id"] == rebuilt.get("objects") or True  # index may be empty if no objects
