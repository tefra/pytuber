import base64
import copy
import json
from datetime import datetime

import pydrag

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
from pytubefm.storage import Registry
from tests.utils import TestCase


class PlaylistTests(TestCase):
    def test_initialization(self):
        playlist = Playlist(
            type="foo", provider="bar", arguments=dict(a=1, b=2), limit=10
        )
        actual = playlist.asdict()
        expected = {
            "arguments": {"a": 1, "b": 2},
            "id": "3bdcfa8",
            "limit": 10,
            "provider": "bar",
            "synced": None,
            "type": "foo",
            "uploaded": None,
            "tracks": [],
            "youtube_id": None,
            "title": None,
        }
        modified = actual.pop("modified")
        self.assertDictEqual(expected, actual)
        self.assertEqual(
            datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M"),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        )
        self.assertEqual(
            "eyJhcmd1bWVudHMiOiB7ImEiOiAxLCAiYiI6IDJ9LCAicHJvdmlkZXIiOiAiYmFyIiwgInR5cGUiOiAiZm9vIn0=",
            playlist.mime,
        )

        expected = {
            "arguments": {"a": 1, "b": 2},
            "provider": "bar",
            "type": "foo",
        }
        self.assertEqual(
            expected, json.loads(base64.b64decode(playlist.mime.encode()))
        )


class TrackTests(TestCase):
    def test_initializations(self):
        track = Track(artist="DMX", name="ruff ryders", duration=None)
        self.assertEqual("c85d968", track.id)


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
        tracks=[],
        youtube_id=None,
        title=None,
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
        PlaylistManager.update(playlist, dict(limit=420, synced=None))
        playlist = PlaylistManager.find(playlist.provider)[0]

        self.assertEqual(420, playlist.limit)
        self.assertIsNone(playlist.synced)

        playlist = PlaylistManager.update(playlist, dict(tracks=[1, 2, 3]))
        self.assertEqual([1, 2, 3], playlist.tracks)
        self.assertIsNotNone(playlist.synced)


class TrackManagerTests(TestCase):
    def test_add(self):
        def track(artist, name, duration):
            return pydrag.Track.from_dict(
                dict(artist=artist, name=name, duration=duration)
            )

        tracks = [
            track("Queen", "Bohemian Rhapsody", 367),
            track("Foo", "Bar", 166),
        ]

        TrackManager.add(tracks)
        actual = Registry.get("tracks")
        expected = {
            "55a4d2b": {
                "id": "55a4d2b",
                "artist": "Queen",
                "duration": 367,
                "name": "Bohemian Rhapsody",
                "youtube_id": None,
            },
            "8843d7f": {
                "id": "8843d7f",
                "artist": "Foo",
                "duration": 166,
                "name": "Bar",
                "youtube_id": None,
            },
        }

        self.assertEqual(expected, actual)

    def test_find(self):
        Registry.set(
            "tracks",
            {
                "55a4d2b": {
                    "id": "55a4d2b",
                    "artist": "Queen",
                    "duration": 367,
                    "name": "Bohemian Rhapsody",
                    "youtube_id": None,
                },
                "8843d7f": {
                    "id": "8843d7f",
                    "artist": "Foo",
                    "duration": 166,
                    "name": "Bar",
                    "youtube_id": None,
                },
            },
        )

        tracks = TrackManager.find(["55a4d2b", "8843d7f"])
        self.assertEqual(2, len(tracks))
        for track in tracks:
            self.assertIsInstance(track, Track)
