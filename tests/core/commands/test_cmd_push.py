from unittest import mock

from pytuber import cli
from pytuber.core.models import PlaylistItem, PlaylistManager, TrackManager
from pytuber.core.services import YouService
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandPushTests(CommandTestCase):
    @mock.patch("pytuber.core.commands.cmd_push.push_tracks")
    @mock.patch("pytuber.core.commands.cmd_push.push_playlists")
    def test_push_all(self, push_playlists, push_tracks):
        self.runner.invoke(cli, ["push", "youtube", "--all"])

        push_playlists.assert_called_once()
        push_tracks.assert_called_once()

    @mock.patch.object(YouService, "create_playlist")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_push_playlists(self, find, update, create_playlist):
        p_one, p_two = PlaylistFixture.get(2)
        find.return_value = [p_one, p_two]
        create_playlist.side_effect = ["y1", "y2"]
        result = self.runner.invoke(
            cli, ["push", "youtube", "--playlists"], catch_exceptions=False
        )

        expected_messages = (
            "Creating playlists",
            "Playlist: {}".format(p_one.title),
            "Playlist: {}".format(p_two.title),
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutputContains(expected_messages, result.output)

        create_playlist.assert_has_calls([mock.call(p_one), mock.call(p_two)])
        update.assert_has_calls(
            [
                mock.call(p_one, dict(youtube_id="y1")),
                mock.call(p_two, dict(youtube_id="y2")),
            ]
        )

    def test_push_playlists_empty_list(self):
        result = self.runner.invoke(
            cli, ["push", "youtube", "--playlists"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertIn("There are no new playlists", result.output)

    @mock.patch("pytuber.core.commands.cmd_push.timestamp")
    @mock.patch.object(YouService, "remove_playlist_item")
    @mock.patch.object(YouService, "create_playlist_item")
    @mock.patch.object(YouService, "get_playlist_items")
    @mock.patch.object(TrackManager, "find")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_push_tracks(
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
        tracks = TrackFixture.get(
            6, youtube_id=["$a", "$b", "$c", "$d", "$e", "$f"]
        )
        p_one, p_two = PlaylistFixture.get(
            2, tracks=[["id_a", "id_b", "id_c"], ["id_d", "id_e", "id_f"]]
        )

        find_playlists.return_value = [p_one, p_two]
        find_tracks.side_effect = [tracks[:3], tracks[3:]]

        get_playlist_items.side_effect = [
            [PlaylistItem(1, "$a"), PlaylistItem(2, "$e")],
            [
                PlaylistItem(1, "$d"),
                PlaylistItem(2, "$e"),
                PlaylistItem(2, "$f"),
            ],
        ]

        result = self.runner.invoke(
            cli, ["push", "youtube", "--tracks"], catch_exceptions=False
        )

        expected_output = (
            "Syncing playlists",
            "Fetching playlist items: title_a",
            "Adding new playlist items",
            "Adding video: $b",
            "Adding video: $c",
            "Removing playlist items",
            "Removing video: $e",
            "Fetching playlist items: title_b",
            "Playlist is already synced!",
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
        remove_playlist_item.assert_called_once_with(PlaylistItem(2, "$e"))
        update_playlist.assert_called_once_with(p_one, dict(uploaded=101))
