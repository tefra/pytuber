from collections import namedtuple
from datetime import timedelta
from unittest import mock

from pydrag import Artist, Tag, Track, User, constants
from pydrag.models.common import ListModel

from pytuber.core.models import ConfigManager, Provider
from pytuber.exceptions import NotFound
from pytuber.lastfm.models import PlaylistType
from pytuber.lastfm.services import LastService
from pytuber.storage import Registry
from tests.utils import TestCase


class LastServiceTests(TestCase):
    def get_user(self):
        return User(
            playlists=1,
            playcount=10000000,
            gender="m",
            name="rj",
            url="",
            country="greece",
            image="",
            age="33",
            registered=1037793040,
        )

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(User, "get_loved_tracks")
    @mock.patch.object(LastService, "get_user")
    def test_sync_with_user_loved_tracks(self, get_user, loved_tracks, *args):
        get_user.return_value = self.get_user()
        loved_tracks.return_value = ListModel(["a", "b", "c"])

        actual = LastService.get_tracks(
            type=PlaylistType.USER_LOVED_TRACKS.value, limit=10, username="foo"
        )
        self.assertEqual(["a", "b", "c"], actual)
        get_user.assert_called_once_with("foo")
        loved_tracks.assert_called_once_with(limit=10)

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(User, "get_recent_tracks")
    @mock.patch.object(LastService, "get_user")
    def test_sync_with_user_recent_tracks(
        self, get_user, recent_tracks, *args
    ):
        get_user.return_value = self.get_user()
        recent_tracks.return_value = ListModel(["a", "b", "c"])

        actual = LastService.get_tracks(
            type=PlaylistType.USER_RECENT_TRACKS.value,
            limit=10,
            username="foo",
        )
        self.assertEqual(["a", "b", "c"], actual)
        get_user.assert_called_once_with("foo")
        recent_tracks.assert_called_once_with(limit=10)

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(User, "get_top_tracks")
    @mock.patch.object(LastService, "get_user")
    def test_sync_with_user_top_tracks(self, get_user, top_tracks, *args):
        get_user.return_value = self.get_user()
        top_tracks.return_value = ListModel(["a", "b", "c"])

        actual = LastService.get_tracks(
            type=PlaylistType.USER_TOP_TRACKS.value, limit=10, username="foo"
        )
        self.assertEqual(["a", "b", "c"], actual)
        get_user.assert_called_once_with("foo")
        top_tracks.assert_called_once_with(
            period=constants.Period.overall, limit=10
        )

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(User, "get_friends")
    @mock.patch.object(LastService, "get_user")
    def test_sync_with_user_friends_tracks(self, get_user, friends, *args):
        get_user.return_value = self.get_user()
        friend = namedtuple("Friend", ["recent_track"])
        friends.return_value = [
            friend(recent_track=1),
            friend(recent_track=2),
            friend(recent_track=3),
        ]

        actual = LastService.get_tracks(
            type=PlaylistType.USER_FRIENDS_RECENT_TRACKS.value,
            limit=10,
            username="foo",
        )
        self.assertEqual([1, 2, 3], actual)
        get_user.assert_called_once_with("foo")
        friends.assert_called_once_with(limit=10, recent_tracks=True)

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(Track, "get_top_tracks_chart")
    def test_sync_with_chart(self, top_tracks_chart, *args):
        top_tracks_chart.return_value = ListModel(["a", "b", "c"])
        actual = LastService.get_tracks(
            type=PlaylistType.CHART.value, limit=10
        )
        self.assertEqual(["a", "b", "c"], actual)
        top_tracks_chart.assert_called_once_with(limit=10)

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(Track, "get_top_tracks_by_country")
    def test_sync_with_country_chart(self, top_tracks_by_country, *args):
        top_tracks_by_country.return_value = ListModel(["a", "b", "c"])
        actual = LastService.get_tracks(
            type=PlaylistType.COUNTRY.value, limit=10, country="greece"
        )
        self.assertEqual(["a", "b", "c"], actual)
        top_tracks_by_country.assert_called_once_with(
            limit=10, country="greece"
        )

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(Tag, "get_top_tracks")
    @mock.patch.object(LastService, "get_tag")
    def test_sync_with_tag_chart(self, get_tag, get_top_tracks, *args):
        get_tag.return_value = Tag(name="rock")
        get_top_tracks.return_value = ListModel(["a", "b", "c"])
        actual = LastService.get_tracks(
            type=PlaylistType.TAG.value, limit=10, tag="rock"
        )
        self.assertEqual(["a", "b", "c"], actual)
        get_tag.assert_called_once_with("rock")
        get_top_tracks.assert_called_once_with(limit=10)

    @mock.patch.object(LastService, "assert_config")
    @mock.patch.object(Artist, "get_top_tracks")
    @mock.patch.object(LastService, "get_artist")
    def test_sync_with_artist_chart(self, get_artist, get_top_tracks, *args):
        get_artist.return_value = Artist(name="queen")
        get_top_tracks.return_value = ListModel(["a", "b", "c"])
        actual = LastService.get_tracks(
            type=PlaylistType.ARTIST.value, limit=10, artist="queeen"
        )
        self.assertEqual(["a", "b", "c"], actual)
        get_artist.assert_called_once_with("queeen")
        get_top_tracks.assert_called_once_with(limit=10)

    @mock.patch.object(LastService, "assert_config")
    @mock.patch("pytuber.storage.time.time")
    @mock.patch.object(Tag, "get_top_tags")
    def test_get_tags(self, get_top_tags, time, assert_config):
        time.return_value = 1

        get_top_tags.side_effect = [
            [Tag(name=i) for i in range(0, 250)],
            [Tag(name=i) for i in range(250, 500)],
            [Tag(name=i) for i in range(500, 750)],
            [Tag(name=i) for i in range(750, 1000)],
        ]

        names = [t.name for t in LastService.get_tags()]
        self.assertEqual(list(range(0, 1000)), names)

        get_top_tags.assert_has_calls(
            [
                mock.call(limit=250, page=1),
                mock.call(limit=250, page=2),
                mock.call(limit=250, page=3),
                mock.call(limit=250, page=4),
            ]
        )

        tags, ttl = Registry.get("last.fm_tag_list")
        self.assertEqual(1000, len(tags))
        self.assertEqual({"name": 0}, tags[0])
        self.assertEqual(timedelta(days=30, seconds=1).total_seconds(), ttl)
        assert_config.assert_called_once()

    @mock.patch.object(LastService, "assert_config")
    @mock.patch("pytuber.storage.time.time")
    @mock.patch.object(Artist, "find")
    def test_get_artist(self, find, time, assert_config):
        time.return_value = 1

        find.return_value = Artist(name="Queen")

        artist = LastService.get_artist("quueee")
        self.assertEqual(Artist(name="Queen"), artist)

        find.assert_called_once_with("quueee")

        artist, ttl = Registry.get("last.fm_artist_quueee")
        self.assertEqual({"name": "Queen"}, artist)

        self.assertEqual(timedelta(days=30, seconds=1).total_seconds(), ttl)
        assert_config.assert_called_once()

    @mock.patch.object(LastService, "assert_config")
    @mock.patch("pytuber.storage.time.time")
    @mock.patch.object(User, "find")
    def test_get_user(self, find, time, assert_config):
        time.return_value = 1
        my_user = self.get_user()
        find.return_value = my_user

        self.assertEqual(my_user, LastService.get_user("rj"))

        find.assert_called_once_with("rj")

        user, ttl = Registry.get("last.fm_user_rj")
        self.assertEqual(self.get_user().to_dict(), user)

        self.assertEqual(timedelta(hours=24, seconds=1).total_seconds(), ttl)
        assert_config.assert_called_once()

    @mock.patch("pytuber.lastfm.services.configure")
    def test_assert_config(self, configure):
        with self.assertRaises(NotFound):
            LastService.assert_config()

        ConfigManager.set(
            dict(provider=Provider.lastfm, data=dict(api_key="aaa"))
        )
        LastService.assert_config()
        configure.assert_called_once_with(api_key="aaa")
