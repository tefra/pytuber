from unittest import mock

import pydrag

from pytuber import cli
from pytuber.core.models import PlaylistManager, Provider, TrackManager
from pytuber.lastfm.commands.cmd_fetch import fetch_tracks
from pytuber.lastfm.services import LastService
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandFetchTests(CommandTestCase):
    @mock.patch("click.secho")
    @mock.patch("click.Abort")
    def test_with_nothing(self, abort, secho):
        result = self.runner.invoke(
            cli, ["fetch", "lastfm"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutputContains("", result.output)
        abort.assert_called_once_with()
        self.assertEqual(1, secho.call_count)

    @mock.patch.object(TrackManager, "set")
    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "get_tracks")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_with_tracks(self, find, update, get_tracks, get_tags, set):

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

        result = self.runner.invoke(cli, ["fetch", "lastfm", "--tracks"])

        self.assertEqual(0, result.exit_code)
        get_tags.assert_called_once_with()
        find.assert_called_once_with(provider=Provider.lastfm)
        get_tracks.assert_has_calls(
            [mock.call(a=0, type="type_a"), mock.call(b=1, type="type_b")]
        )
        set.assert_has_calls(
            [
                mock.call({"artist": "artist_a", "name": "name_a"}),
                mock.call({"artist": "artist_b", "name": "name_b"}),
                mock.call({"artist": "artist_c", "name": "name_c"}),
                mock.call({"artist": "artist_d", "name": "name_d"}),
                mock.call({"artist": "artist_e", "name": "name_e"}),
                mock.call({"artist": "artist_f", "name": "name_f"}),
            ]
        )

        update.assert_has_calls(
            [
                mock.call(playlists[0], dict(tracks=["id_a", "id_b", "id_c"])),
                mock.call(playlists[1], dict(tracks=["id_d", "id_e", "id_f"])),
            ]
        )

    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_with_tags(self, _, get_tags):
        get_tags.return_value = [
            pydrag.Tag(name="rock", count=1, reach=2),
            pydrag.Tag(name="rap", count=2, reach=4),
            pydrag.Tag(name="metal", count=3, reach=6),
        ]
        result = self.runner.invoke(cli, ["fetch", "lastfm", "--tags"])
        expected_output = (
            "No  Name      Count    Reach",
            "----  ------  -------  -------",
            "   0  rock          1        2",
            "   1  rap           2        4",
            "   2  metal         3        6",
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        get_tags.assert_called_once_with()

    @mock.patch.object(PlaylistManager, "find")
    @mock.patch.object(LastService, "get_tags")
    def test_fetch_tracks_with_arguments(self, get_tags, find):
        fetch_tracks(1, 2)

        kwargs = find.call_args_list[0][1]
        self.assertEqual(Provider.lastfm, kwargs["provider"])

        self.assertTrue(kwargs["id"](1))
        self.assertTrue(kwargs["id"](2))
        self.assertFalse(kwargs["id"](3))
