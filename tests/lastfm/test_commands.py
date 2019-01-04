import datetime
from unittest import mock

import click
from pydrag import Artist, Tag

from pytubefm import cli
from pytubefm.exceptions import RecordExists
from pytubefm.lastfm.commands import create_or_update_playlist
from pytubefm.lastfm.models import ChartPlaylist, UserPlaylist
from pytubefm.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
)
from pytubefm.lastfm.services import LastService
from pytubefm.models import Config, Playlist, Provider
from tests.utils import CommandTestCase

fixed_date = datetime.datetime(2000, 12, 12, 12, 12, 12)


class CreateOrUpdatePlaylistTests(CommandTestCase):
    @mock.patch.object(click, "secho")
    @mock.patch.object(Playlist, "save")
    def test_create(self, save, secho):
        playlist = Playlist(type="a", provider="b", limit=10, id="c")
        create_or_update_playlist(playlist)

        save.assert_called_once_with()
        secho.assert_called_once_with("Added playlist: c!")

    @mock.patch.object(click, "secho")
    @mock.patch.object(click, "confirm")
    @mock.patch.object(Playlist, "save")
    def test_update(self, save, confirm, secho):
        save.side_effect = [RecordExists("foo"), None]
        confirm.return_value = True

        playlist = Playlist(type="a", provider="b", limit=10, id="c")
        create_or_update_playlist(playlist)

        save.assert_has_calls([mock.call(), mock.call(overwrite=True)])
        confirm.assert_called_once_with(
            "Overwrite existing playlist?", abort=True
        )
        secho.assert_called_once_with("Updated playlist: c!")


class CommandSetupTests(CommandTestCase):
    def test_create(self):
        self.assertIsNone(Config.find_by_provider(Provider.lastfm))
        result = self.runner.invoke(cli, ["lastfm", "setup"], input="aaaa")

        expected_output = "\n".join(
            ("Last.fm Api Key: aaaa", "Last.fm configuration updated!")
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

        actual = Config.find_by_provider(Provider.lastfm)
        self.assertDictEqual({"api_key": "aaaa"}, actual.data)

    def test_update(self):
        Config(
            provider=Provider.lastfm.value, data=dict(api_key="bbbb")
        ).save()

        self.assertEqual(
            dict(api_key="bbbb"), Config.find_by_provider(Provider.lastfm).data
        )
        result = self.runner.invoke(
            cli, ["lastfm", "setup"], input="\n".join(("aaaa", "y"))
        )

        expected_output = "\n".join(
            (
                "Last.fm Api Key: aaaa",
                "Overwrite existing configuration? [y/N]: y",
                "Last.fm configuration updated!",
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

        actual = Config.find_by_provider(Provider.lastfm)
        self.assertDictEqual({"api_key": "aaaa"}, actual.data)


class CommandAddTests(CommandTestCase):
    @mock.patch("pytubefm.lastfm.commands.create_or_update_playlist")
    def test_user(self, create_or_update):
        result = self.runner.invoke(
            cli, ["lastfm", "add", "user"], input="\n".join(("aaa", "2", "50"))
        )

        expected_output = "\n".join(
            (
                "Last.fm username: aaa",
                "Playlist Types",
                "[1] user_loved_tracks",
                "[2] user_top_tracks",
                "[3] user_recent_tracks",
                "[4] user_friends_recent_tracks",
                "Select a playlist type 1-4: 2",
                "Maximum tracks [50]: 50",
            )
        )

        create_or_update.assert_called_once_with(
            Playlist(
                type=UserPlaylist.TOP_TRACKS,
                provider=Provider.lastfm,
                arguments=dict(username="aaa"),
                limit=50,
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

    @mock.patch("pytubefm.lastfm.commands.create_or_update_playlist")
    def test_chart(self, create_or_update):
        result = self.runner.invoke(
            cli, ["lastfm", "add", "chart"], input="50"
        )

        expected_output = "Maximum tracks [50]: 50"
        create_or_update.assert_called_once_with(
            Playlist(
                type=ChartPlaylist.CHART, provider=Provider.lastfm, limit=50
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

    @mock.patch.object(CountryParamType, "convert")
    @mock.patch("pytubefm.lastfm.commands.create_or_update_playlist")
    def test_country(self, create_or_update, country_param_type):
        country_param_type.return_value = "greece"
        result = self.runner.invoke(
            cli, ["lastfm", "add", "country"], input="gr\n50"
        )

        expected_output = "\n".join(
            ("Country Code: gr", "Maximum tracks [50]: 50")
        )
        create_or_update.assert_called_once_with(
            Playlist(
                type=ChartPlaylist.COUNTRY,
                provider=Provider.lastfm,
                arguments=dict(country="greece"),
                limit=50,
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

    @mock.patch.object(TagParamType, "convert")
    @mock.patch("pytubefm.lastfm.commands.create_or_update_playlist")
    def test_tag(self, create_or_update, tag_param):
        tag_param.return_value = Tag(name="rock")
        result = self.runner.invoke(
            cli, ["lastfm", "add", "tag"], input="rock\n50"
        )

        expected_output = "\n".join(("Tag: rock", "Maximum tracks [50]: 50"))
        create_or_update.assert_called_once_with(
            Playlist(
                type=ChartPlaylist.TAG,
                provider=Provider.lastfm,
                arguments=dict(tag="rock"),
                limit=50,
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

    @mock.patch.object(ArtistParamType, "convert")
    @mock.patch("pytubefm.lastfm.commands.create_or_update_playlist")
    def test_artist(self, create_or_update, artist_param):
        artist_param.return_value = Artist(name="Queen")
        result = self.runner.invoke(
            cli, ["lastfm", "add", "artist"], input="Queen\n50"
        )

        expected_output = "\n".join(
            ("Artist: Queen", "Maximum tracks [50]: 50")
        )
        create_or_update.assert_called_once_with(
            Playlist(
                type=ChartPlaylist.ARTIST,
                provider=Provider.lastfm,
                arguments=dict(artist="Queen"),
                limit=50,
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())


class CommandTagsTests(CommandTestCase):
    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_default(self, _, get_tags):
        get_tags.return_value = [
            Tag(name="rock", count=1, reach=2),
            Tag(name="rap", count=2, reach=4),
            Tag(name="metal", count=3, reach=6),
        ]
        result = self.runner.invoke(cli, ["lastfm", "tags"])

        expected_output = "\n".join(
            (
                "No  Name      Count    Reach",
                "----  ------  -------  -------",
                "   0  rock          1        2",
                "   1  rap           2        4",
                "   2  metal         3        6",
            )
        )
        get_tags.assert_called_once_with(refresh=False)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_force_refresh(self, _, get_tags):
        result = self.runner.invoke(cli, ["lastfm", "tags", "--refresh"])

        get_tags.assert_called_once_with(refresh=True)
        self.assertEqual(0, result.exit_code)


class CommandListPlaylistsTests(CommandTestCase):
    @mock.patch.object(Playlist, "values_header")
    @mock.patch.object(Playlist, "find_by_provider")
    def test_list(self, find, header):
        header.return_value = ["a", "b", "c"]
        p_one = mock.Mock()
        p_one.values_list.return_value = [1, 2, 3]
        p_two = mock.Mock()
        p_two.values_list.return_value = [4, 5, 6]

        find.return_value = [p_one, p_two]

        result = self.runner.invoke(cli, ["lastfm", "list"])

        expected_output = "\n".join(
            ("a    b    c", "---  ---  ---", "  1    2    3", "  4    5    6")
        )
        find.assert_called_once_with(Provider.lastfm)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())


class CommandRemovePlaylistTests(CommandTestCase):
    @mock.patch.object(Playlist, "remove")
    @mock.patch.object(Playlist, "get")
    def test_remove(self, get, remove):
        playlist = Playlist(provider=Provider.lastfm, limit=1, type="foo")
        get.return_value = playlist

        result = self.runner.invoke(
            cli, ["lastfm", "remove", "foo"], input="y"
        )

        expected_output = "\n".join(
            ("Do you want to continue? [y/N]: y", "Removed playlist: 0863aa0!")
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())
        get.assert_called_once_with(provider=Provider.lastfm, id="foo")
        remove.assert_called_once_with()

    @mock.patch.object(Playlist, "remove")
    @mock.patch.object(Playlist, "get")
    def test_remove_no_confirm(self, get, remove):
        playlist = Playlist(provider=Provider.lastfm, limit=1, type="foo")
        get.return_value = playlist

        result = self.runner.invoke(
            cli, ["lastfm", "remove", "foo"], input="n"
        )

        expected_output = "\n".join(
            ("Do you want to continue? [y/N]: n", "Aborted!")
        )
        self.assertEqual(1, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())
        get.assert_called_once_with(provider=Provider.lastfm, id="foo")
        self.assertEqual(0, remove.call_count)
