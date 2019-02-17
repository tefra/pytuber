import base64
import json
from datetime import datetime

import attr

from pytuber.core.models import (
    Config,
    ConfigManager,
    Document,
    Manager,
    Playlist,
    PlaylistManager,
    PlaylistType,
    Provider,
    StrEnum,
    Track,
    TrackManager,
)
from pytuber.exceptions import NotFound
from pytuber.storage import Registry
from tests.utils import PlaylistFixture, TestCase, TrackFixture


class PlaylistTests(TestCase):
    def test_initialization(self):
        playlist = PlaylistFixture.one()
        actual = playlist.asdict()
        expected = {
            "type": "type_a",
            "provider": "provider_a",
            "arguments": {"a": 0},
            "id": "id_a",
            "title": "title_a",
            "youtube_id": None,
            "tracks": [],
            "synced": None,
            "uploaded": None,
        }
        self.assertDictEqual(expected, actual)
        expected = (
            "eyJhcmd1bWVudHMiOiB7ImEiOiAwfSwgInByb3ZpZGVyIjogInByb3ZpZG"
            "VyX2EiLCAidHlwZSI6ICJ0eXBlX2EiLCAidGl0bGUiOiAidGl0bGVfYSJ9"
        )
        self.assertEqual(expected, playlist.mime)

        expected = {
            "arguments": {"a": 0},
            "provider": "provider_a",
            "type": "type_a",
            "title": "title_a",
        }
        self.assertEqual(
            expected, json.loads(base64.b64decode(playlist.mime.encode()))
        )


class TrackTests(TestCase):
    def test_initializations(self):
        track = TrackFixture.one(id=None)
        self.assertEqual("6784d47", track.id)


class ProviderTests(TestCase):
    def test_youtube(self):
        self.assertEqual("youtube", str(Provider.youtube))
        self.assertEqual(Provider.youtube.value, str(Provider.youtube))

    def test_lastfm(self):
        self.assertEqual("last.fm", str(Provider.lastfm))
        self.assertEqual(Provider.lastfm.value, str(Provider.lastfm))


@attr.s(auto_attribs=True)
class Foo(Document):
    id: str
    value: int
    keeper: str = attr.ib(default=None, metadata=dict(keep=True))


class FooManager(Manager):
    namespace = "foo"
    key = "id"
    model = Foo


class ManagerTests(TestCase):
    data = dict(id="a", value=1, keeper="keep")

    def test_get(self):
        with self.assertRaises(NotFound) as cm:
            FooManager.get("bar")
        self.assertEqual(
            "No foo matched your argument: bar!", str(cm.exception)
        )

        Registry.set("foo", "bar", self.data)
        obj = FooManager.get("bar")
        self.assertIsInstance(obj, FooManager.model)
        self.assertDictEqual(self.data, obj.asdict())

    def test_set(self):
        foo = FooManager.set(self.data)
        self.assertIsInstance(foo, FooManager.model)
        self.assertDictEqual(self.data, Registry.get("foo", "a"))
        self.assertDictEqual(self.data, foo.asdict())

        bar = FooManager.set(dict(id="a", value=1))
        self.assertEqual(foo.asdict(), bar.asdict())

        thug = FooManager.set(dict(id="a", value=1, keeper="peek"))
        self.assertEqual("peek", thug.keeper)

    def test_update(self):
        foo = FooManager.set(self.data)
        new_foo = FooManager.update(foo, dict(value=2))

        self.assertIsNot(foo, new_foo)
        self.assertIsInstance(new_foo, FooManager.model)

        expected = dict(id="a", value=2, keeper="keep")
        self.assertDictEqual(expected, Registry.get("foo", "a"))
        self.assertDictEqual(expected, new_foo.asdict())

    def test_remove(self):
        Registry.set("foo", "bar", "dummy")
        FooManager.remove("bar")
        with self.assertRaises(NotFound) as cm:
            FooManager.remove("bar")
        self.assertEqual(
            "No foo matched your argument: bar!", str(cm.exception)
        )

    def test_find(self):
        a = FooManager.set(dict(id="a", value=1))
        b = FooManager.set(dict(id="b", value=2))
        c = FooManager.set(dict(id="c", value=2))
        d = FooManager.set(dict(id="d", value=1))
        e = FooManager.set(dict(id="e", value=None))

        self.assertEqual([a, b, c, d, e], FooManager.find())
        self.assertEqual([b, c], FooManager.find(value=2))
        self.assertEqual([c], FooManager.find(value=2, id="c"))
        self.assertEqual([], FooManager.find(id="x"))
        self.assertEqual([e], FooManager.find(value=None))
        self.assertEqual([a, d], FooManager.find(value=lambda x: x == 1))

    def test_exists(self):
        a = Foo(id="a", value=1)
        self.assertFalse(FooManager.exists(a))

        FooManager.set(a.asdict())
        self.assertTrue(FooManager.exists(a))


class ConfigManagerTests(TestCase):
    def test_class(self):
        self.assertTrue(issubclass(ConfigManager, Manager))
        self.assertEqual(Config, ConfigManager.model)
        self.assertEqual("provider", ConfigManager.key)
        self.assertEqual("configuration", ConfigManager.namespace)


class PlaylistManagerTests(TestCase):
    def test_class(self):
        self.assertTrue(issubclass(PlaylistManager, Manager))
        self.assertEqual(Playlist, PlaylistManager.model)
        self.assertEqual("id", PlaylistManager.key)
        self.assertEqual("playlist", PlaylistManager.namespace)

    def test_update_sets_synced_if_tracks_are_updated(self):
        playlist = PlaylistManager.set(
            dict(id=1, type=None, provider=None, title="foo")
        )

        new = PlaylistManager.update(playlist, dict(tracks=[1, 2, 3]))
        self.assertEqual(
            datetime.fromtimestamp(new.synced).strftime("%Y-%m-%d %H:%M"),
            datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        )


class TrackManagerTests(TestCase):
    def test_class(self):
        self.assertTrue(issubclass(TrackManager, Manager))
        self.assertEqual(Track, TrackManager.model)
        self.assertEqual("id", TrackManager.key)
        self.assertEqual("track", TrackManager.namespace)

    def test_find_youtube_id(self):
        Registry.set("track", "a", "youtube_id", 1)
        self.assertEqual(1, TrackManager.find_youtube_id("a"))
        self.assertIsNone(TrackManager.find_youtube_id("b"))


class PlaylistTypeTests(TestCase):
    def test_enum(self):
        self.assertTrue(issubclass(PlaylistType, StrEnum))
        for c in PlaylistType:
            self.assertEqual(str(c), c.value)
