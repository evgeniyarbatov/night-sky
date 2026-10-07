import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.inspire import existing_apod_dates, resolve_apod_image, try_apod_image


class ExistingApodDatesTests(unittest.TestCase):
    def test_collects_dates_from_sidecar_json_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            day_dir = Path(tmpdir)
            (day_dir / "a.json").write_text(
                json.dumps(
                    {"title": "A", "date": "2024-01-01", "source_url": "", "image_url": ""}
                ),
                encoding="utf-8",
            )
            (day_dir / "b.json").write_text(
                json.dumps(
                    {"title": "B", "date": "2024-01-02", "source_url": "", "image_url": ""}
                ),
                encoding="utf-8",
            )
            found = existing_apod_dates(day_dir)

        self.assertEqual(found, {"2024-01-01", "2024-01-02"})

    def test_returns_empty_set_when_directory_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            found = existing_apod_dates(Path(tmpdir) / "does-not-exist")
        self.assertEqual(found, set())


class TryApodImageTests(unittest.TestCase):
    def test_returns_none_without_calling_fetch_when_date_excluded(self) -> None:
        with mock.patch("scripts.inspire.fetch_apod") as mock_fetch:
            result = try_apod_image("2024-01-01", sess=mock.Mock(), exclude_dates={"2024-01-01"})

        mock_fetch.assert_not_called()
        self.assertIsNone(result)

    def test_returns_data_when_image_with_url(self) -> None:
        data = {"media_type": "image", "hdurl": "https://example.com/x.jpg"}
        with mock.patch("scripts.inspire.fetch_apod", return_value=data):
            result = try_apod_image("2024-01-01", sess=mock.Mock(), exclude_dates=set())

        self.assertEqual(result, data)

    def test_returns_none_when_media_type_is_video(self) -> None:
        data = {"media_type": "video", "url": "https://example.com/x.mp4"}
        with mock.patch("scripts.inspire.fetch_apod", return_value=data):
            result = try_apod_image("2024-01-01", sess=mock.Mock(), exclude_dates=set())

        self.assertIsNone(result)

    def test_returns_none_when_image_has_no_url(self) -> None:
        data = {"media_type": "image"}
        with mock.patch("scripts.inspire.fetch_apod", return_value=data):
            result = try_apod_image("2024-01-01", sess=mock.Mock(), exclude_dates=set())

        self.assertIsNone(result)


class ResolveApodImageTests(unittest.TestCase):
    def test_returns_first_successful_recent_day(self) -> None:
        data = {"media_type": "image", "hdurl": "https://example.com/x.jpg"}
        with mock.patch("scripts.inspire.fetch_apod", return_value=data):
            result, sess = resolve_apod_image(exclude_dates=set())

        self.assertEqual(result, data)
        self.assertIsNotNone(sess)

    def test_falls_back_to_random_sample_when_recent_days_are_videos(self) -> None:
        video = {"media_type": "video"}
        image = {"media_type": "image", "hdurl": "https://example.com/x.jpg"}
        with mock.patch("scripts.inspire.fetch_apod", side_effect=[video, video, image]):
            result, _ = resolve_apod_image(exclude_dates=set(), max_back_days=1, random_attempts=5)

        self.assertEqual(result, image)

    def test_raises_when_no_image_found_anywhere(self) -> None:
        with (
            mock.patch("scripts.inspire.fetch_apod", return_value={"media_type": "video"}),
            self.assertRaises(RuntimeError),
        ):
            resolve_apod_image(exclude_dates=set(), max_back_days=0, random_attempts=3)

    def test_propagates_last_error_message_when_all_attempts_fail(self) -> None:
        with (
            mock.patch("scripts.inspire.fetch_apod", side_effect=RuntimeError("network down")),
            self.assertRaises(RuntimeError) as err,
        ):
            resolve_apod_image(exclude_dates=set(), max_back_days=0, random_attempts=2)

        self.assertIn("network down", str(err.exception))


if __name__ == "__main__":
    unittest.main()
