import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.common import (
    ImageMeta,
    apod_to_meta,
    classify_destination,
    copy_with_sidecars,
    download_file,
    fetch_apod,
    go_deeper_text,
    library_item_to_meta,
    library_search,
    load_meta,
    nasa_api_key,
    pick_image_asset,
    resolve_library_image_url,
    safe_filename,
    write_sidecar,
)


class SafeFilenameTests(unittest.TestCase):
    def test_strips_forbidden_characters(self) -> None:
        self.assertEqual(safe_filename('a<b>c:d"e/f\\g|h?i*j'), "abcdefghij")

    def test_collapses_whitespace_and_replaces_with_underscore(self) -> None:
        self.assertEqual(safe_filename("  hello   world  "), "hello_world")

    def test_collapses_repeated_underscores(self) -> None:
        self.assertEqual(safe_filename("a___b"), "a_b")

    def test_truncates_to_max_len(self) -> None:
        self.assertEqual(len(safe_filename("x" * 200, max_len=10)), 10)

    def test_empty_result_falls_back_to_untitled(self) -> None:
        self.assertEqual(safe_filename("???"), "untitled")


class ClassifyDestinationTests(unittest.TestCase):
    def test_body_hint_direct_term_match(self) -> None:
        self.assertEqual(classify_destination(body_hint="titan"), "gas-giants")

    def test_body_hint_homonym_mercury_is_other(self) -> None:
        self.assertEqual(classify_destination(body_hint="mercury"), "other")

    def test_body_hint_gas_giant_name(self) -> None:
        self.assertEqual(classify_destination(body_hint="jupiter"), "gas-giants")

    def test_body_hint_mars(self) -> None:
        self.assertEqual(classify_destination(body_hint="mars"), "mars")

    def test_body_hint_moon_vs_earth(self) -> None:
        self.assertEqual(classify_destination(body_hint="moon"), "moon")
        self.assertEqual(classify_destination(body_hint="earth"), "earth-from-space")

    def test_scores_by_title_and_description_when_no_hint(self) -> None:
        dest = classify_destination(
            title="Saturn's rings in stunning detail",
            description="A view of the rings of Saturn from Cassini",
        )
        self.assertEqual(dest, "gas-giants")

    def test_title_hit_outweighs_a_single_description_hit(self) -> None:
        dest = classify_destination(
            title="Comet streaks across the sky",
            description="a nebula glimpsed in the background",
        )
        self.assertEqual(dest, "comets-asteroids")

    def test_defaults_to_other_when_nothing_matches(self) -> None:
        self.assertEqual(classify_destination(title="", description=""), "other")


class GoDeeperTextTests(unittest.TestCase):
    def test_returns_stripped_description_when_present(self) -> None:
        self.assertEqual(go_deeper_text("  a real caption  ", "Title"), "a real caption")

    def test_falls_back_to_title_based_message_when_empty(self) -> None:
        text = go_deeper_text("", "My Title")
        self.assertIn("My Title", text)


class PickImageAssetTests(unittest.TestCase):
    def test_prefers_orig_or_large_jpg(self) -> None:
        assets = [
            "https://example.com/thumb.jpg",
            "https://example.com/image~small.jpg",
            "https://example.com/image~orig.jpg",
        ]
        self.assertEqual(pick_image_asset(assets), "https://example.com/image~orig.jpg")

    def test_falls_back_to_any_image_extension(self) -> None:
        assets = ["https://example.com/metadata.json", "https://example.com/photo.png"]
        self.assertEqual(pick_image_asset(assets), "https://example.com/photo.png")

    def test_returns_none_when_no_image_asset(self) -> None:
        assets = ["https://example.com/metadata.json", "https://example.com/video.mp4"]
        self.assertIsNone(pick_image_asset(assets))


class NasaApiKeyTests(unittest.TestCase):
    def test_uses_env_var_when_set(self) -> None:
        with mock.patch.dict(os.environ, {"NASA_API_KEY": "  real-key  "}):
            self.assertEqual(nasa_api_key(), "real-key")

    def test_falls_back_to_demo_key_when_unset(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(nasa_api_key(), "DEMO_KEY")


class ApodToMetaTests(unittest.TestCase):
    def test_builds_meta_with_source_url_from_date(self) -> None:
        data = {
            "title": "A Nice Nebula",
            "explanation": "Some nebula explanation.",
            "hdurl": "https://apod.nasa.gov/apod/image/hd.jpg",
            "date": "2024-03-05",
        }
        meta = apod_to_meta(data)
        self.assertEqual(meta.title, "A Nice Nebula")
        self.assertEqual(meta.image_url, "https://apod.nasa.gov/apod/image/hd.jpg")
        self.assertEqual(meta.source_url, "https://apod.nasa.gov/apod/ap240305.html")
        self.assertEqual(meta.nasa_id, "apod-2024-03-05")
        self.assertEqual(meta.credit, "APOD / NASA")
        self.assertEqual(meta.destination, "nebulae")

    def test_prefers_url_over_hdurl_absence_and_marks_copyright(self) -> None:
        data = {
            "title": "Some Image",
            "explanation": "",
            "url": "https://apod.nasa.gov/apod/image/sd.jpg",
            "date": "2024-01-01",
            "copyright": "Jane Doe",
        }
        meta = apod_to_meta(data)
        self.assertEqual(meta.image_url, "https://apod.nasa.gov/apod/image/sd.jpg")
        self.assertEqual(meta.credit, "APOD / Jane Doe")
        self.assertIn("Jane Doe", meta.license)

    def test_missing_date_falls_back_to_generic_source_url(self) -> None:
        meta = apod_to_meta({"title": "No Date", "explanation": "x"})
        self.assertEqual(meta.source_url, "https://apod.nasa.gov/apod/")
        self.assertEqual(meta.nasa_id, "apod")


class LibraryItemToMetaTests(unittest.TestCase):
    def test_extracts_fields_from_nasa_library_item(self) -> None:
        item = {
            "data": [
                {
                    "title": "Mars Surface Panorama",
                    "description": "A panorama of the Martian surface.",
                    "keywords": ["Mars", "Surface"],
                    "nasa_id": "PIA12345",
                    "date_created": "2020-05-01T00:00:00Z",
                    "center": "JPL",
                }
            ]
        }
        meta = library_item_to_meta(
            item, image_url="https://example.com/mars.jpg", search_term="mars", body="mars"
        )
        self.assertEqual(meta.title, "Mars Surface Panorama")
        self.assertEqual(meta.date, "2020-05-01")
        self.assertEqual(meta.nasa_id, "PIA12345")
        self.assertEqual(meta.credit, "NASA/JPL")
        self.assertEqual(meta.source_url, "https://images.nasa.gov/details/PIA12345")
        self.assertEqual(meta.destination, "mars")

    def test_missing_nasa_id_falls_back_to_generic_source_url(self) -> None:
        item = {"data": [{"title": "Untitled"}]}
        meta = library_item_to_meta(item, image_url="https://example.com/x.jpg")
        self.assertEqual(meta.source_url, "https://images.nasa.gov")
        self.assertEqual(meta.credit, "NASA")


class SidecarRoundTripTests(unittest.TestCase):
    def test_write_then_load_round_trips_known_fields(self) -> None:
        meta = ImageMeta(
            title="Test Image",
            date="2024-01-01",
            source_url="https://example.com/src",
            image_url="https://example.com/img.jpg",
            keywords=["a", "b"],
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "photo.jpg"
            image_path.write_bytes(b"fake-bytes")

            json_path, md_path = write_sidecar(image_path, meta)

            self.assertTrue(json_path.is_file())
            self.assertTrue(md_path.is_file())

            loaded = load_meta(image_path)

        assert loaded is not None
        self.assertEqual(loaded.title, "Test Image")
        self.assertEqual(loaded.keywords, ["a", "b"])
        self.assertEqual(loaded.local_image, "photo.jpg")

    def test_write_sidecar_fills_default_go_deeper(self) -> None:
        meta = ImageMeta(
            title="No Caption",
            date="",
            source_url="",
            image_url="",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "photo.jpg"
            write_sidecar(image_path, meta)
            loaded = load_meta(image_path)

        assert loaded is not None
        self.assertIn("No Caption", loaded.go_deeper)

    def test_load_meta_ignores_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = Path(tmpdir) / "photo.jpg"
            json_path = image_path.with_suffix(".json")
            json_path.write_text(
                json.dumps(
                    {
                        "title": "X",
                        "date": "",
                        "source_url": "",
                        "image_url": "",
                        "some_future_field": "surprise",
                    }
                ),
                encoding="utf-8",
            )
            loaded = load_meta(image_path)

        assert loaded is not None
        self.assertEqual(loaded.title, "X")

    def test_load_meta_returns_none_when_sidecar_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertIsNone(load_meta(Path(tmpdir) / "missing.jpg"))


class CopyWithSidecarsTests(unittest.TestCase):
    def test_copies_image_and_existing_sidecars(self) -> None:
        meta = ImageMeta(title="Copy Me", date="2024-01-01", source_url="s", image_url="i")
        with tempfile.TemporaryDirectory() as tmpdir:
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            dest_dir = Path(tmpdir) / "dest"
            image_path = src_dir / "photo.jpg"
            image_path.write_bytes(b"fake-bytes")
            write_sidecar(image_path, meta)

            result = copy_with_sidecars(image_path, dest_dir)

            self.assertEqual(result, dest_dir / "photo.jpg")
            self.assertTrue((dest_dir / "photo.jpg").is_file())
            self.assertTrue((dest_dir / "photo.json").is_file())
            self.assertTrue((dest_dir / "photo.md").is_file())


class DownloadFileTests(unittest.TestCase):
    def test_writes_response_content_to_filepath(self) -> None:
        fake_response = mock.Mock()
        fake_response.raise_for_status = mock.Mock()
        fake_response.iter_content = mock.Mock(return_value=[b"a", b"b"])
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(return_value=fake_response)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "sub" / "out.jpg"
            download_file("https://example.com/x.jpg", filepath, sess=fake_session)
            self.assertEqual(filepath.read_bytes(), b"ab")

        fake_session.get.assert_called_once_with(
            "https://example.com/x.jpg", stream=True, timeout=30
        )

    def test_raises_after_exhausting_retries(self) -> None:
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(side_effect=RuntimeError("boom"))

        with (
            tempfile.TemporaryDirectory() as tmpdir,
            mock.patch("scripts.common.time.sleep"),
            self.assertRaises(RuntimeError) as err,
        ):
            download_file(
                "https://example.com/x.jpg",
                Path(tmpdir) / "out.jpg",
                sess=fake_session,
                retries=2,
            )

        self.assertEqual(fake_session.get.call_count, 2)
        self.assertIn("boom", str(err.exception))


class FetchApodTests(unittest.TestCase):
    def test_builds_request_with_api_key_and_date(self) -> None:
        fake_response = mock.Mock()
        fake_response.raise_for_status = mock.Mock()
        fake_response.json = mock.Mock(return_value={"title": "X"})
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(return_value=fake_response)

        data = fetch_apod(date="2024-01-01", api_key="mykey", sess=fake_session)

        self.assertEqual(data, {"title": "X"})
        fake_session.get.assert_called_once_with(
            "https://api.nasa.gov/planetary/apod",
            params={"api_key": "mykey", "date": "2024-01-01"},
            timeout=20,
        )

    def test_omits_date_param_when_not_given(self) -> None:
        fake_response = mock.Mock()
        fake_response.raise_for_status = mock.Mock()
        fake_response.json = mock.Mock(return_value={})
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(return_value=fake_response)

        fetch_apod(api_key="mykey", sess=fake_session)

        _, kwargs = fake_session.get.call_args
        self.assertNotIn("date", kwargs["params"])


class LibrarySearchTests(unittest.TestCase):
    def test_parses_items_and_total_hits(self) -> None:
        fake_response = mock.Mock()
        fake_response.raise_for_status = mock.Mock()
        fake_response.json = mock.Mock(
            return_value={
                "collection": {
                    "items": [{"data": [{"title": "a"}]}],
                    "metadata": {"total_hits": 42},
                }
            }
        )
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(return_value=fake_response)

        items, total = library_search("mars", sess=fake_session)

        self.assertEqual(len(items), 1)
        self.assertEqual(total, 42)

    def test_missing_collection_data_defaults_to_empty(self) -> None:
        fake_response = mock.Mock()
        fake_response.raise_for_status = mock.Mock()
        fake_response.json = mock.Mock(return_value={})
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(return_value=fake_response)

        items, total = library_search("mars", sess=fake_session)

        self.assertEqual(items, [])
        self.assertEqual(total, 0)


class ResolveLibraryImageUrlTests(unittest.TestCase):
    def test_returns_none_when_item_has_no_href(self) -> None:
        self.assertIsNone(resolve_library_image_url({}, sess=mock.Mock()))

    def test_returns_none_when_assets_response_is_not_a_list(self) -> None:
        fake_response = mock.Mock()
        fake_response.raise_for_status = mock.Mock()
        fake_response.json = mock.Mock(return_value={"not": "a list"})
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(return_value=fake_response)

        result = resolve_library_image_url({"href": "https://x"}, sess=fake_session)

        self.assertIsNone(result)

    def test_picks_best_asset_from_list(self) -> None:
        fake_response = mock.Mock()
        fake_response.raise_for_status = mock.Mock()
        fake_response.json = mock.Mock(return_value=["https://x/thumb.jpg", "https://x/orig.jpg"])
        fake_session = mock.Mock()
        fake_session.get = mock.Mock(return_value=fake_response)

        result = resolve_library_image_url({"href": "https://x"}, sess=fake_session)

        self.assertEqual(result, "https://x/orig.jpg")


if __name__ == "__main__":
    unittest.main()
