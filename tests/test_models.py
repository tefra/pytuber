import copy
from datetime import datetime

import pydrag

from pytubefm.data import Registry
from pytubefm.exceptions import NotFound
from pytubefm.models import (
    Config,
    ConfigManager,
    Playlist,
    PlaylistManager,
    Provider,
    Track,
    TrackManager,
)
from tests.utils import TestCase


class PlaylistTests(TestCase):
    def test_initialization(self):
        actual = Playlist(
            type="foo", provider="bar", arguments=dict(a=1, b=2), limit=10
        ).asdict()
        expected = {
            "arguments": {"a": 1, "b": 2},
            "id": "3bdcfa8",
            "limit": 10,
            "provider": "bar",
            "synced": None,
            "type": "foo",
            "uploaded": None,
        }
        modified = actual.pop("modified")
        self.assertDictEqual(expected, actual)
        self.assertEqual(
            datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M"),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        )


class ProviderTests(TestCase):
    def test_youtube(self):
        self.assertEqual("youtube", str(Provider.youtube))
        self.assertEqual(Provider.youtube.value, str(Provider.youtube))

    def test_lastfm(self):
        self.assertEqual("last.fm", str(Provider.lastfm))
        self.assertEqual(Provider.lastfm.value, str(Provider.lastfm))


class ConfigManagerTests(TestCase):
    def test_get(self):
        self.assertIsNone(ConfigManager.get("foo"))

        data = {"data": {"a": 1}, "provider": "foo"}
        Registry.set("provider_config_foo", data)
        actual = ConfigManager.get("foo")

        self.assertIsInstance(actual, Config)
        self.assertEqual(data, actual.asdict())

    def test_update(self):
        ConfigManager.update(dict(provider="foo", data=dict(a=1)))
        expected = {"data": {"a": 1}, "provider": "foo"}
        self.assertEqual(expected, Registry.get("provider_config_foo"))


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

    def test_update(self):
        playlist = PlaylistManager.set(self.data)
        PlaylistManager.update(playlist, dict(limit=420))
        playlist = PlaylistManager.find(playlist.provider)[0]
        self.assertEqual(420, playlist.limit)


class TrackManagerTests(TestCase):
    def test_set(self):
        playlist = PlaylistManager.set(
            dict(
                type="foo", provider="bar", arguments=dict(a=1, b=2), limit=10
            )
        )

        def track(artist, name, duration):
            return pydrag.Track.from_dict(
                dict(artist=artist, name=name, duration=duration)
            )

        tracks = [
            track("Queen", "Bohemian Rhapsody", 367),
            track("Foo", "Bar", 166),
        ]

        TrackManager.set(playlist, tracks)
        actual = Registry.get("playlist_tracks_%s" % playlist.id)
        expected = [
            {"artist": "Queen", "duration": 367, "name": "Bohemian Rhapsody"},
            {"artist": "Foo", "duration": 166, "name": "Bar"},
        ]

        self.assertEqual(expected, actual)

        playlist = PlaylistManager.get("bar", "3bdcfa8")
        self.assertEqual(
            datetime.fromtimestamp(playlist.modified).strftime(
                "%Y-%m-%d %H:%M"
            ),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        )

    def test_find(self):
        self.assertEqual([], TrackManager.find("foo"))
        Registry.set(
            "playlist_tracks_foo",
            [
                {
                    "artist": "Queen",
                    "duration": 367,
                    "name": "Bohemian Rhapsody",
                },
                {"artist": "Foo", "duration": 166, "name": "Bar"},
            ],
        )

        tracks = TrackManager.find("foo")
        self.assertEqual(2, len(tracks))
        for track in tracks:
            self.assertIsInstance(track, Track)

    def test_remove(self):
        Registry.set(
            "playlist_tracks_foo",
            [
                {
                    "artist": "Queen",
                    "duration": 367,
                    "name": "Bohemian Rhapsody",
                }
            ],
        )

        self.assertEqual(1, len(TrackManager.find("foo")))
        TrackManager.remove("foo")
        self.assertEqual([], TrackManager.find("foo"))
        TrackManager.remove("foo")  # Doesn't raise exception!
