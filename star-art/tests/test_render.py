import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
spec = importlib.util.spec_from_file_location("render_script", SCRIPTS_DIR / "render.py")
assert spec is not None and spec.loader is not None
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


class TestRender(unittest.TestCase):
    def test_list_styles_names_every_script_style(self) -> None:
        names = {s["name"] for s in render.list_styles()}
        self.assertIn("sumi", names)
        self.assertIn("wabi-sabi-stars", names)
        self.assertIn("horizon-slice", names)
        self.assertEqual(len(names), 9)

    def test_catalog_styles_resolve_to_script_constants(self) -> None:
        for name in render.STYLES:
            if name in ("sumi", "sumi-stars", "wabi-sabi-stars", "sumi-planets", "horizon-slice"):
                continue
            kind = name.removeprefix("sumi-")
            self.assertTrue((SCRIPTS_DIR / f"star-art-{kind}.py").exists(), name)

    def test_unknown_style_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sky = Path(tmp) / "sky.json"
            sky.write_text(json.dumps({"name": "x", "lat": 0, "lon": 0, "date": "2026-01-01"}))
            with self.assertRaises(ValueError):
                render.render(1, {"style": "nope"}, sky, Path(tmp), "preview")

    def test_star_names_csv_is_found(self) -> None:
        self.assertTrue(render._star_names_csv().exists())


if __name__ == "__main__":
    unittest.main()
