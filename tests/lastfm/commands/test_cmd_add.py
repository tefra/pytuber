from unittest import mock

from pytuber import cli
from pytuber.core.models import PlaylistManager, Provider
from pytuber.lastfm.models import PlaylistType, UserPlaylistType
from pytuber.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
    UserParamType,
)
from tests.utils import CommandTestCase, PlaylistFixture


class CommandAddTests(CommandTestCase):
    @mock.patch("pytuber.lastfm.commands.cmd_add.fetch_tracks")
    @mock.patch.object(UserParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_user_playlist(self, create_playlist, convert, fetch_tracks):
        convert.return_value = "bbb"
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli,
            ["add", "lastfm", "user-playlist"],
            input="\n".join(("aaa", "2", "50", "My Favorite  ")),
            catch_exceptions=False,
        )

        expected_output = (
            "Last.fm username: aaa",
            "Playlist Types",
            "[1] User Loved Tracks",
            "[2] User Top Tracks",
            "[3] User Recent Tracks",
            "[4] User Friends Recent Tracks",
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
        fetch_tracks.assert_called_once_with("id_a")

    @mock.patch("pytuber.lastfm.commands.cmd_add.fetch_tracks")
    @mock.patch.object(PlaylistManager, "set")
    def test_chart_playlist(self, create_playlist, fetch_tracks):
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli, ["add", "lastfm", "chart-playlist"], input="50\n "
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
        fetch_tracks.assert_called_once_with("id_a")

    @mock.patch("pytuber.lastfm.commands.cmd_add.fetch_tracks")
    @mock.patch.object(CountryParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_country_playlist(
        self, create_playlist, country_param_type, fetch_tracks
    ):
        country_param_type.return_value = "greece"
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli, ["add", "lastfm", "country-playlist"], input=b"gr\n50\n "
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
        fetch_tracks.assert_called_once_with("id_a")

    @mock.patch("pytuber.lastfm.commands.cmd_add.fetch_tracks")
    @mock.patch.object(TagParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_tag_playlist(self, create_playlist, convert, fetch_tracks):
        convert.return_value = "rock"
        create_playlist.return_value = PlaylistFixture.one(synced=111)
        result = self.runner.invoke(
            cli, ["add", "lastfm", "tag-playlist"], input="rock\n50\n "
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
        fetch_tracks.assert_called_once_with("id_a")

    @mock.patch("pytuber.lastfm.commands.cmd_add.fetch_tracks")
    @mock.patch.object(ArtistParamType, "convert")
    @mock.patch.object(PlaylistManager, "set")
    def test_artist_playlist(
        self, create_playlist, artist_param, fetch_tracks
    ):
        artist_param.return_value = "Queen"
        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli,
            ["add", "lastfm", "artist-playlist"],
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
        fetch_tracks.assert_called_once_with("id_a")
