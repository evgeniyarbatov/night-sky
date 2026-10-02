import unittest

from scripts.stars import is_deep_sky_photo


def _item(title: str, description: str = "", keywords: list[str] | None = None) -> dict:
    return {"data": [{"title": title, "description": description, "keywords": keywords or []}]}


class IsDeepSkyPhotoTests(unittest.TestCase):
    def test_telescope_photo_of_nebula_is_kept(self) -> None:
        self.assertTrue(is_deep_sky_photo(_item("Hubble reveals heart of Lagoon Nebula")))

    def test_subject_must_be_in_title(self) -> None:
        self.assertFalse(is_deep_sky_photo(_item("Hubble Friday", "a nebula seen by hubble")))

    def test_needs_a_telescope_credit(self) -> None:
        self.assertFalse(is_deep_sky_photo(_item("Carina Nebula Detail", "ground observatory")))

    def test_hardware_and_data_products_are_dropped(self) -> None:
        self.assertFalse(is_deep_sky_photo(_item("Webb mirror segment views a star")))
        self.assertFalse(is_deep_sky_photo(_item("Spectrum of a Hubble galaxy")))
        self.assertFalse(is_deep_sky_photo(_item("Artist concept of a star", keywords=["Webb"])))

    def test_composite_graphics_are_dropped(self) -> None:
        item = _item("Tracing Hubble galaxies", "examples of galaxies arranged by time")
        self.assertFalse(is_deep_sky_photo(item))


if __name__ == "__main__":
    unittest.main()
