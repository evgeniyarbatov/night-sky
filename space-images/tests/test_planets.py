import json
import tempfile
import unittest
from pathlib import Path

from scripts.planets import PlanetImageDownloader, _has_term, _item_nasa_id


def _item(
    title: str = "", description: str = "", keywords: list[str] | None = None, nasa_id: str = ""
) -> dict:
    return {
        "data": [
            {
                "title": title,
                "description": description,
                "keywords": keywords or [],
                "nasa_id": nasa_id,
            }
        ]
    }


class HasTermTests(unittest.TestCase):
    def test_short_ambiguous_term_requires_word_boundary(self) -> None:
        self.assertTrue(_has_term("a field of rock and dust", "rock"))
        self.assertFalse(_has_term("the rocket launched", "rock"))

    def test_multi_word_term_is_substring_match(self) -> None:
        self.assertTrue(_has_term("seen from orbit today", "from orbit"))


class ItemNasaIdTests(unittest.TestCase):
    def test_extracts_nasa_id_from_data_block(self) -> None:
        self.assertEqual(_item_nasa_id(_item(nasa_id="PIA00001")), "PIA00001")

    def test_missing_data_block_returns_empty_string(self) -> None:
        self.assertEqual(_item_nasa_id({}), "")


class IsValidPlanetImageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.downloader = PlanetImageDownloader(download_dir=self.tmpdir.name)

    def test_accepts_title_with_planet_name_and_body_term(self) -> None:
        item = _item(title="Mars Surface Panorama", description="A view of the martian terrain.")
        self.assertTrue(self.downloader.is_valid_planet_image(item, "mars"))

    def test_rejects_when_planet_name_absent_from_title(self) -> None:
        item = _item(title="A distant world", description="surface terrain")
        self.assertFalse(self.downloader.is_valid_planet_image(item, "mars"))

    def test_rejects_global_exclude_terms(self) -> None:
        item = _item(title="Mars surface", description="Artist concept of a rover")
        self.assertFalse(self.downloader.is_valid_planet_image(item, "mars"))

    def test_rejects_planet_specific_exclude_terms(self) -> None:
        item = _item(title="Project Mercury capsule splashdown")
        self.assertFalse(self.downloader.is_valid_planet_image(item, "mercury"))

    def test_rejects_when_moon_named_in_title(self) -> None:
        item = _item(title="Titan seen near Saturn", description="ring terrain")
        self.assertFalse(self.downloader.is_valid_planet_image(item, "saturn"))

    def test_rejects_crewed_context_for_non_earth_planet(self) -> None:
        item = _item(title="Mars from the International Space Station")
        self.assertFalse(self.downloader.is_valid_planet_image(item, "mars"))

    def test_allows_crewed_context_for_earth(self) -> None:
        item = _item(
            title="Earth from the International Space Station",
            description="The blue marble seen from orbit.",
        )
        self.assertTrue(self.downloader.is_valid_planet_image(item, "earth"))

    def test_accepts_mission_hit_with_keyword_and_body_term(self) -> None:
        item = _item(
            title="Juno captures cloud bands",
            description="",
            keywords=["jupiter"],
        )
        self.assertTrue(self.downloader.is_valid_planet_image(item, "jupiter"))

    def test_accepts_short_portrait_title_without_body_terms(self) -> None:
        item = _item(title="Full Blue Mars")
        self.assertTrue(self.downloader.is_valid_planet_image(item, "mars"))

    def test_rejects_long_title_without_body_terms_or_portrait_words(self) -> None:
        item = _item(title="Engineers inspecting the Mars helicopter hardware today")
        self.assertFalse(self.downloader.is_valid_planet_image(item, "mars"))


class ExistingNasaIdsTests(unittest.TestCase):
    def test_collects_nasa_ids_from_sidecar_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = PlanetImageDownloader(download_dir=tmpdir)
            planet_dir = Path(tmpdir) / "mars"
            planet_dir.mkdir()
            (planet_dir / "a.json").write_text(
                json.dumps(
                    {
                        "title": "A",
                        "date": "",
                        "source_url": "",
                        "image_url": "",
                        "nasa_id": "PIA001",
                    }
                ),
                encoding="utf-8",
            )
            (planet_dir / "b.json").write_text(
                json.dumps(
                    {
                        "title": "B",
                        "date": "",
                        "source_url": "",
                        "image_url": "",
                        "nasa_id": "PIA002",
                    }
                ),
                encoding="utf-8",
            )

            found = downloader.existing_nasa_ids(planet_dir)

        self.assertEqual(found, {"PIA001", "PIA002"})

    def test_returns_empty_set_when_directory_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = PlanetImageDownloader(download_dir=tmpdir)
            found = downloader.existing_nasa_ids(Path(tmpdir) / "does-not-exist")
        self.assertEqual(found, set())


if __name__ == "__main__":
    unittest.main()
