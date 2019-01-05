import copy
from unittest import mock

from pytubefm.data import Registry
from pytubefm.exceptions import NotFound
from pytubefm.models import Playlist, PlaylistManager
from tests.utils import TestCase


class PlaylistTests(TestCase):
    @mock.patch("pytubefm.models.timestamp", return_value=528016230)
    def setUp(self, now):
        super(PlaylistTests, self).setUp()
        self.playlist = Playlist(
            type="foo", provider="bar", arguments=dict(a=1, b=2), limit=10
        )

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


class PlaylistManagerTests(TestCase):
    data = dict(
        id="a",
        type="foo",
        provider="bar",
        arguments=dict(a=1, b=2),
        limit=10,
        modified=11111111,
        synced=2222222,
        uploaded=333333,
    )

    def test_get(self):
        with self.assertRaises(NotFound) as cm:
            PlaylistManager.get("foo", "bar")
        self.assertEqual("No such playlist id: bar!", str(cm.exception))

        Registry.set("provider_playlists_foo", "bar", self.data)
        playlist = PlaylistManager.get("foo", "bar")
        self.assertIsInstance(playlist, Playlist)
        self.assertDictEqual(self.data, playlist.asdict())

    def test_set(self):
        playlist = PlaylistManager.set(self.data)
        self.assertIsInstance(playlist, Playlist)
        self.assertDictEqual(self.data, playlist.asdict())

        new_data = copy.deepcopy(self.data)
        new_data.update(dict(synced=False, uploaded=False))

        playlist = PlaylistManager.set(new_data)
        self.assertIsInstance(playlist, Playlist)
        self.assertDictEqual(self.data, playlist.asdict())

    def test_find(self):
        self.assertEqual([], PlaylistManager.find("bar"))

        for i in range(0, 3):
            data = copy.deepcopy(self.data)
            data.update(dict(id=i))
            PlaylistManager.set(data)

        playlists = PlaylistManager.find("bar")
        self.assertEqual(3, len(playlists))
        self.assertEqual([0, 1, 2], [p.id for p in playlists])

    def test_remove(self):
        Registry.set("provider_playlists_foo", "bar", "dummy")
        PlaylistManager.remove("foo", "bar")

        with self.assertRaises(NotFound) as cm:
            PlaylistManager.remove("foo", "bar")
        self.assertEqual("No such playlist id: bar!", str(cm.exception))
