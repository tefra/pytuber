from datetime import datetime, timedelta, timezone
from unittest import mock

from pytubefm.exceptions import NotFound, RecordExists
from pytubefm.models import Playlist, Storage
from tests.utils import TestCase

fixed_date = datetime(2000, 12, 12, 12, 12, 12, tzinfo=timezone.utc)


class DocumentTests(TestCase):
    def test_now(self):
        now = datetime.now()
        actual = Storage.now()
        self.assertIsInstance(actual, datetime)
        self.assertGreaterEqual(actual, now)
        self.assertLess(actual, now + timedelta(seconds=1))


class PlaylistTests(TestCase):
    @mock.patch.object(Playlist, "now", return_value=fixed_date)
    def setUp(self, now):
        super(PlaylistTests, self).setUp()
        self.playlist = Playlist(
            type="foo", provider="bar", arguments=dict(a=1, b=2), limit=10
        )

    def test_save_new(self):
        self.playlist.save()
        expected = {
            "playlist_bar": {
                "c6dbb2e": {
                    "id": "c6dbb2e",
                    "arguments": {"a": 1, "b": 2},
                    "limit": 10,
                    "modified": 976623132,
                    "provider": "bar",
                    "synced": None,
                    "type": "foo",
                    "uploaded": None,
                }
            }
        }
        self.assertDictEqual(expected, Playlist.storage().db)

    def test_save_existing_raises_exception(self):
        self.playlist.save()

        with self.assertRaises(RecordExists) as cm:
            self.playlist.save()
        self.assertEqual("Playlist already exists!", str(cm.exception))

    def test_save_existing_with_overwrite_true(self):
        self.playlist.synced = 1
        self.playlist.save()

        self.playlist.synced = 0
        self.playlist.save(overwrite=True)

        expected = {
            "playlist_bar": {
                "c6dbb2e": {
                    "id": "c6dbb2e",
                    "arguments": {"a": 1, "b": 2},
                    "limit": 10,
                    "modified": 976623132,
                    "provider": "bar",
                    "synced": 1,
                    "type": "foo",
                    "uploaded": None,
                }
            }
        }
        self.assertDictEqual(expected, Playlist.storage().db)

    def test_remove(self):
        self.assertEqual(0, len(Playlist.find_by_provider("bar")))

        self.playlist.save()
        self.assertEqual(1, len(Playlist.find_by_provider("bar")))

        self.assertTrue(self.playlist.remove())
        self.assertEqual(0, len(Playlist.find_by_provider("bar")))

        with self.assertRaises(NotFound) as cm:
            self.playlist.remove()
        self.assertEqual("No such playlist id: c6dbb2e!", str(cm.exception))

    def test_values_list(self):
        self.assertEqual(
            self.playlist.values_list(),
            ("c6dbb2e", "Foo", "a: 1, b: 2", 10, "2000-12-12 12:12", "-", "-"),
        )

        self.playlist.synced = int(
            (fixed_date + timedelta(hours=12)).strftime("%s")
        )
        self.playlist.uploaded = int(
            (fixed_date + timedelta(hours=24)).strftime("%s")
        )
        self.assertEqual(
            self.playlist.values_list(),
            (
                "c6dbb2e",
                "Foo",
                "a: 1, b: 2",
                10,
                "2000-12-12 12:12",
                "2000-12-13 00:12",
                "2000-12-13 12:12",
            ),
        )

    def test_values_header(self):
        expected = (
            "ID",
            "Type",
            "Arguments",
            "Limit",
            "Modified",
            "Synced",
            "Uploaded",
        )
        self.assertEqual(expected, Playlist.values_header())
