from datetime import datetime, timezone
from unittest import mock

from pytubefm.exceptions import NotFound, RecordExists
from pytubefm.models import Document, Playlist, Storage
from tests.utils import TestCase

fixed_datetime = datetime(1986, 9, 25, 10, 10, 30, tzinfo=timezone.utc)


class DocumentTests(TestCase):
    def test_now(self):
        actual = Document.now()
        self.assertIsInstance(actual, datetime)


class PlaylistTests(TestCase):
    @mock.patch.object(Playlist, "now", return_value=fixed_datetime)
    def setUp(self, now):
        super(PlaylistTests, self).setUp()
        self.playlist = Playlist(
            type="foo", provider="bar", arguments=dict(a=1, b=2), limit=10
        )

    def test_save_new(self):
        self.playlist.save()
        expected = {
            "id": "c6dbb2e",
            "arguments": {"a": 1, "b": 2},
            "limit": 10,
            "modified": int(fixed_datetime.strftime("%s")),
            "provider": "bar",
            "synced": None,
            "type": "foo",
            "uploaded": None,
        }
        self.assertDictEqual(expected, Storage.get("playlist_bar", "c6dbb2e"))

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
            "id": "c6dbb2e",
            "arguments": {"a": 1, "b": 2},
            "limit": 10,
            "modified": int(fixed_datetime.strftime("%s")),
            "provider": "bar",
            "synced": 1,
            "type": "foo",
            "uploaded": None,
        }
        self.assertDictEqual(expected, Storage.get("playlist_bar", "c6dbb2e"))

    def test_remove(self):
        self.assertEqual(0, len(Playlist.find_by_provider("bar")))

        self.playlist.save()
        self.assertEqual(1, len(Playlist.find_by_provider("bar")))

        self.playlist.remove()
        self.assertEqual(0, len(Playlist.find_by_provider("bar")))

        with self.assertRaises(NotFound) as cm:
            self.playlist.remove()
        self.assertEqual("No such playlist id: c6dbb2e!", str(cm.exception))

    def test_values_list(self):

        self.playlist.synced = self.playlist.modified + 12 * 60 * 60
        self.playlist.uploaded = self.playlist.modified + 24 * 60 * 60
        self.assertEqual(
            self.playlist.values_list(),
            (
                "c6dbb2e",
                "Foo",
                "a: 1, b: 2",
                10,
                Playlist.date(self.playlist.modified),
                Playlist.date(self.playlist.synced),
                Playlist.date(self.playlist.uploaded),
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
