from unittest import mock

from pytuber import cli
from pytuber.core.models import PlaylistManager, TrackManager
from pytuber.core.services import YouService
from tests.utils import (
    CommandTestCase,
    PlaylistFixture,
    PlaylistItemFixture,
    TrackFixture,
)


class CommandFetchTests(CommandTestCase):
    @mock.patch("click.secho")
    @mock.patch("click.Abort")
    def test_with_nothing(self, abort, secho):
        result = self.runner.invoke(
            cli, ["fetch", "youtube"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutputContains("", result.output)
        abort.assert_called_once_with()
        self.assertEqual(1, secho.call_count)

    @mock.patch("pytuber.core.commands.cmd_fetch.fetch_tracks")
    @mock.patch("pytuber.core.commands.cmd_fetch.fetch_playlists")
    def test_all(self, fetch_playlists, fetch_tracks):
        self.runner.invoke(cli, ["fetch", "youtube", "--all"])

        fetch_playlists.assert_called_once()
        fetch_tracks.assert_called_once()

    @mock.patch.object(TrackManager, "update")
    @mock.patch.object(YouService, "search_track")
    @mock.patch.object(TrackManager, "find")
    def test_fetch_tracks(self, find, search, update):
        track_one, track_two = TrackFixture.get(2)
        find.return_value = [track_one, track_two]

        search.side_effect = ["y1", "y3"]
        result = self.runner.invoke(
            cli, ["fetch", "youtube", "--tracks"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        find.assert_called_once_with(youtube_id=None)
        search.assert_has_calls([mock.call(track_one), mock.call(track_two)])
        update.assert_has_calls(
            [
                mock.call(track_one, dict(youtube_id="y1")),
                mock.call(track_two, dict(youtube_id="y3")),
            ]
        )

    @mock.patch.object(TrackManager, "set")
    @mock.patch.object(PlaylistManager, "exists")
    @mock.patch.object(PlaylistManager, "set")
    @mock.patch.object(YouService, "get_playlist_items")
    @mock.patch.object(YouService, "get_playlists")
    def test_fetch_playlists(
        self,
        get_playlists,
        get_playlist_items,
        set_playlist,
        exists,
        set_tracks,
    ):
        exists.side_effect = [True, False]
        p_one, p_two = PlaylistFixture.get(2)
        v_one, v_two = PlaylistItemFixture.get(2)
        get_playlists.return_value = [p_one, p_two]
        get_playlist_items.return_value = [v_one, v_two]
        set_tracks.side_effect = TrackFixture.get(2)

        result = self.runner.invoke(
            cli, ["fetch", "youtube", "--playlists"], catch_exceptions=False
        )

        expected_messages = ("Fetching playlists info",)
        self.assertEqual(0, result.exit_code)
        self.assertOutputContains(expected_messages, result.output)

        p_two.tracks = ["id_a", "id_b"]
        get_playlists.assert_called_once_with()
        set_playlist.assert_has_calls(
            [mock.call(p_one.asdict()), mock.call(p_two.asdict())]
        )
        set_tracks.assert_has_calls(
            [
                mock.call(
                    {
                        "artist": "artist_a",
                        "name": "name_a",
                        "youtube_id": "video_id_a",
                    }
                ),
                mock.call(
                    {
                        "artist": "artist_b",
                        "name": "name_b",
                        "youtube_id": "video_id_b",
                    }
                ),
            ]
        )
