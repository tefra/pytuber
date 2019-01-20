from unittest import mock

import pydrag

from pytuber import cli
from pytuber.lastfm.models import PlaylistType, UserPlaylistType
from pytuber.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
    UserParamType,
)
from pytuber.lastfm.services import LastService
from pytuber.models import PlaylistManager, Provider, TrackManager
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandAddTests(CommandTestCase):
    @mock.patch.object(UserParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_user(self, create_playlist, convert):
        convert.return_value = "bbb"
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli,
            ["lastfm", "add", "user"],
            input="\n".join(("aaa", "2", "50", "My Favorite  ")),
            catch_exceptions=False,
        )

        expected_output = (
            "Last.fm username: aaa",
            "Playlist Types",
            "[1] user_loved_tracks",
            "[2] user_top_tracks",
            "[3] user_recent_tracks",
            "[4] user_friends_recent_tracks",
            "Select a playlist type 1-4: 2",
            "Maximum tracks [50]: 50",
            "Title: My Favorite  ",
            "Added playlist: id_a!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        create_playlist.assert_called_once_with(
            dict(
                type=UserPlaylistType.USER_TOP_TRACKS,
                provider=Provider.lastfm,
                arguments=dict(limit=50, username="bbb"),
                title="My Favorite",
            )
        )

    @mock.patch.object(PlaylistManager, "set")
    def test_chart(self, create_playlist):
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli, ["lastfm", "add", "chart"], input="50\n "
        )

        expected_output = (
            "Maximum tracks [50]: 50",
            "Title:  ",
            "Added playlist: id_a!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)

        create_playlist.assert_called_once_with(
            dict(
                type=PlaylistType.CHART,
                provider=Provider.lastfm,
                arguments=dict(limit=50),
                title="",
            )
        )

    @mock.patch.object(CountryParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_country(self, create_playlist, country_param_type):
        country_param_type.return_value = "greece"
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli, ["lastfm", "add", "country"], input=b"gr\n50\n "
        )

        expected_output = (
            "Country Code: gr",
            "Maximum tracks [50]: 50",
            "Title:  ",
            "Added playlist: id_a!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        create_playlist.assert_called_once_with(
            dict(
                type=PlaylistType.COUNTRY,
                provider=Provider.lastfm,
                arguments=dict(limit=50, country="greece"),
                title="",
            )
        )

    @mock.patch.object(TagParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_tag(self, create_playlist, convert):
        convert.return_value = "rock"
        create_playlist.return_value = PlaylistFixture.one(synced=111)
        result = self.runner.invoke(
            cli, ["lastfm", "add", "tag"], input="rock\n50\n "
        )

        expected_output = (
            "Tag: rock",
            "Maximum tracks [50]: 50",
            "Title:  ",
            "Updated playlist: id_a!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        create_playlist.assert_called_once_with(
            dict(
                type=PlaylistType.TAG,
                provider=Provider.lastfm,
                arguments=dict(limit=50, tag="rock"),
                title="",
            )
        )

    @mock.patch.object(ArtistParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_artist(self, create_playlist, artist_param):
        artist_param.return_value = "Queen"
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli,
            ["lastfm", "add", "artist"],
            input="Queen\n50\nQueen....",
            catch_exceptions=False,
        )

        expected_output = (
            "Artist: Queen",
            "Maximum tracks [50]: 50",
            "Title: Queen....",
            "Added playlist: id_a!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        create_playlist.assert_called_once_with(
            dict(
                type=PlaylistType.ARTIST,
                provider=Provider.lastfm,
                arguments=dict(limit=50, artist="Queen"),
                title="Queen....",
            )
        )


class CommandTagsTests(CommandTestCase):
    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_default(self, _, get_tags):
        get_tags.return_value = [
            pydrag.Tag(name="rock", count=1, reach=2),
            pydrag.Tag(name="rap", count=2, reach=4),
            pydrag.Tag(name="metal", count=3, reach=6),
        ]
        result = self.runner.invoke(cli, ["lastfm", "tags"])
        expected_output = (
            "No  Name      Count    Reach",
            "----  ------  -------  -------",
            "   0  rock          1        2",
            "   1  rap           2        4",
            "   2  metal         3        6",
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        get_tags.assert_called_once_with(refresh=False)

    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_force_refresh(self, _, get_tags):
        result = self.runner.invoke(cli, ["lastfm", "tags", "--refresh"])

        self.assertEqual(0, result.exit_code)
        get_tags.assert_called_once_with(refresh=True)


class CommandSyncPlaylistsTests(CommandTestCase):
    @mock.patch.object(TrackManager, "set")
    @mock.patch.object(LastService, "get_tracks")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_sync_all(self, find, update, get_tracks, set):

        tracks = TrackFixture.get(6)
        playlists = PlaylistFixture.get(2)
        last_tracks = [
            pydrag.Track.from_dict(dict(name=track.name, artist=track.artist))
            for track in tracks
        ]

        set.side_effect = tracks
        find.return_value = playlists
        get_tracks.side_effect = [
            [last_tracks[0], last_tracks[1], last_tracks[2]],
            [last_tracks[3], last_tracks[4], last_tracks[5]],
        ]

        result = self.runner.invoke(
            cli, ["lastfm", "sync"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        find.assert_called_once_with(provider=Provider.lastfm)
        get_tracks.assert_has_calls(
            [mock.call(a=0, type="type_a"), mock.call(b=1, type="type_b")]
        )
        set.assert_has_calls(
            [
                mock.call(
                    {"artist": "artist_a", "name": "name_a", "duration": None}
                ),
                mock.call(
                    {"artist": "artist_b", "name": "name_b", "duration": None}
                ),
                mock.call(
                    {"artist": "artist_c", "name": "name_c", "duration": None}
                ),
                mock.call(
                    {"artist": "artist_d", "name": "name_d", "duration": None}
                ),
                mock.call(
                    {"artist": "artist_e", "name": "name_e", "duration": None}
                ),
                mock.call(
                    {"artist": "artist_f", "name": "name_f", "duration": None}
                ),
            ]
        )

        update.assert_has_calls(
            [
                mock.call(playlists[0], dict(tracks=["id_a", "id_b", "id_c"])),
                mock.call(playlists[1], dict(tracks=["id_d", "id_e", "id_f"])),
            ]
        )

    @mock.patch.object(TrackManager, "set")
    @mock.patch.object(LastService, "get_tracks")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_sync_one(self, find, update, get_tracks, set):
        tracks = TrackFixture.get(3)
        playlists = PlaylistFixture.get(2)
        last_tracks = [
            pydrag.Track.from_dict(dict(name=track.name, artist=track.artist))
            for track in tracks
        ]

        set.side_effect = tracks
        find.return_value = playlists
        get_tracks.side_effect = [
            [last_tracks[0], last_tracks[1], last_tracks[2]]
        ]

        result = self.runner.invoke(
            cli, ["lastfm", "sync", playlists[1].id], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        find.assert_called_once_with(provider=Provider.lastfm)
        get_tracks.assert_called_once_with(b=1, type="type_b")
        set.assert_has_calls(
            [
                mock.call(
                    {"artist": "artist_a", "name": "name_a", "duration": None}
                ),
                mock.call(
                    {"artist": "artist_b", "name": "name_b", "duration": None}
                ),
                mock.call(
                    {"artist": "artist_c", "name": "name_c", "duration": None}
                ),
            ]
        )

        update.assert_called_once_with(
            playlists[1], dict(tracks=["id_a", "id_b", "id_c"])
        )
