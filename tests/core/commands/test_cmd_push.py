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


class CommandPushTests(CommandTestCase):
    @mock.patch("click.secho")
    @mock.patch("click.Abort")
    def test_with_nothing(self, abort, secho):
        result = self.runner.invoke(
            cli, ["push", "youtube"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutputContains("", result.output)
        abort.assert_called_once_with()
        self.assertEqual(1, secho.call_count)

    @mock.patch("pytuber.core.commands.cmd_push.push_tracks")
    @mock.patch("pytuber.core.commands.cmd_push.push_playlists")
    def test_with_all(self, push_playlists, push_tracks):
        self.runner.invoke(cli, ["push", "youtube", "--all"])

        push_playlists.assert_called_once()
        push_tracks.assert_called_once()

    @mock.patch.object(YouService, "create_playlist")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_with_playlists(self, find, update, create_playlist):
        p_one, p_two = PlaylistFixture.get(2)
        find.return_value = [p_one, p_two]
        create_playlist.side_effect = ["y1", "y2"]
        result = self.runner.invoke(
            cli, ["push", "youtube", "--playlists"], catch_exceptions=False
        )

        expected_messages = ("Creating playlists: 2/2",)
        self.assertEqual(0, result.exit_code)
        self.assertOutputContains(expected_messages, result.output)

        create_playlist.assert_has_calls([mock.call(p_one), mock.call(p_two)])
        update.assert_has_calls(
            [
                mock.call(p_one, dict(youtube_id="y1")),
                mock.call(p_two, dict(youtube_id="y2")),
            ]
        )

    @mock.patch("pytuber.core.commands.cmd_push.timestamp")
    @mock.patch.object(YouService, "remove_playlist_item")
    @mock.patch.object(YouService, "create_playlist_item")
    @mock.patch.object(YouService, "get_playlist_items")
    @mock.patch.object(TrackManager, "find")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_with_tracks(
        self,
        find_playlists,
        update_playlist,
        find_tracks,
        get_playlist_items,
        create_playlist_item,
        remove_playlist_item,
        timestamp,
    ):

        timestamp.return_value = 101
        items = PlaylistItemFixture.get(4, video_id=["$a", "$d", "$e", "$f"])

        tracks = TrackFixture.get(
            6, youtube_id=["$a", "$b", "$c", "$d", "$e", "$f"]
        )
        p_one, p_two = PlaylistFixture.get(
            2, tracks=[["id_a", "id_b", "id_c"], ["id_d", "id_e", "id_f"]]
        )

        find_playlists.return_value = [p_one, p_two]
        find_tracks.side_effect = [tracks[:3], tracks[3:]]

        get_playlist_items.side_effect = [
            [items[0], items[2]],
            [items[1], items[2], items[3]],
        ]

        result = self.runner.invoke(
            cli, ["push", "youtube", "--tracks"], catch_exceptions=False
        )

        expected_output = (
            "Syncing playlists",
            "Fetching playlist items: title_a",
            "Adding new playlist items: 2",
            "Removing playlist items: 1",
            "Fetching playlist items: title_b",
            "Adding new playlist items",
            "Removing playlist items",
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutputContains(expected_output, result.output)

        get_playlist_items.assert_has_calls(
            [mock.call(p_one), mock.call(p_two)]
        )

        create_playlist_item.assert_has_calls(
            [
                mock.call(p_one, tracks[1].youtube_id),
                mock.call(p_one, tracks[2].youtube_id),
            ]
        )
        remove_playlist_item.assert_called_once_with(items[2])
        update_playlist.assert_called_once_with(p_one, dict(uploaded=101))
