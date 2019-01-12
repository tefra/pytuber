from unittest import mock

from google.oauth2.credentials import Credentials

from pytuber import cli
from pytuber.models import (
    ConfigManager,
    PlaylistManager,
    Provider,
    TrackManager,
)
from pytuber.youtube.models import PlaylistItem
from pytuber.youtube.services import YouService
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandSetupTests(CommandTestCase):
    @mock.patch.object(YouService, "authorize")
    def test_create(self, authorize):
        authorize.return_value = Credentials(
            token="token",
            token_uri="token_uri",
            client_id="client_id",
            client_secret="client_secret",
            scopes="scopes",
        )

        self.assertIsNone(ConfigManager.get(Provider.youtube, default=None))
        client_secrets = "~/Downloads/client_secrets.json"
        result = self.runner.invoke(cli, ["youtube", "setup", client_secrets])

        authorize.assert_called_once_with(client_secrets)
        self.assertEqual(0, result.exit_code)

        expected = {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": None,
            "scopes": "scopes",
            "token_uri": "token_uri",
        }
        actual = ConfigManager.get(Provider.youtube)
        self.assertDictEqual(expected, actual.data)

    def test_update(self):
        ConfigManager.set(dict(provider=Provider.youtube, data="foo"))
        client_secrets = "~/Downloads/client_secrets.json"
        result = self.runner.invoke(
            cli, ["youtube", "setup", client_secrets], input="n"
        )

        expected_output = "\n".join(
            ("Overwrite existing configuration? [y/N]: n", "Aborted!")
        )
        self.assertEqual(1, result.exit_code)
        self.assertIn(expected_output, result.output.strip())


class CommandGroupFetchTests(CommandTestCase):
    @mock.patch.object(TrackManager, "update")
    @mock.patch.object(YouService, "search_track")
    @mock.patch.object(TrackManager, "find")
    def test_tracks(self, find, search, update):
        track_one, track_two = TrackFixture.get(2)
        find.return_value = [track_one, track_two]

        search.side_effect = ["y1", "y3"]
        result = self.runner.invoke(
            cli, ["youtube", "fetch", "tracks"], catch_exceptions=False
        )

        expected_messages = (
            "Fetching tracks information",
            "Track: artist_a - name_a",
            "Track: artist_b - name_b",
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutputContains(expected_messages, result.output)

        find.assert_called_once_with(youtube_id=None)
        search.assert_has_calls([mock.call(track_one), mock.call(track_two)])
        update.assert_has_calls(
            [
                mock.call(track_one, dict(youtube_id="y1")),
                mock.call(track_two, dict(youtube_id="y3")),
            ]
        )

    def test_tracks_empty_list(self):
        result = self.runner.invoke(
            cli, ["youtube", "fetch", "tracks"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertIn("There are no new tracks", result.output)

    @mock.patch.object(PlaylistManager, "set")
    @mock.patch.object(YouService, "get_playlists")
    def test_playlists(self, get_playlists, set_playlist):
        p_one, p_two = PlaylistFixture.get(2)
        get_playlists.return_value = [p_one, p_two]

        result = self.runner.invoke(
            cli, ["youtube", "fetch", "playlists"], catch_exceptions=False
        )

        expected_messages = (
            "Imported playlist {}".format(p_one.id),
            "Imported playlist {}".format(p_two.id),
            "Fetching playlists information",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutputContains(expected_messages, result.output)

        get_playlists.assert_called_once_with()
        set_playlist.assert_has_calls(
            [mock.call(p_one.asdict()), mock.call(p_two.asdict())]
        )


class CommandGroupPushTests(CommandTestCase):
    @mock.patch.object(YouService, "create_playlist")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_playlists(self, find, update, create_playlist):
        p_one, p_two = PlaylistFixture.get(2)
        find.return_value = [p_one, p_two]
        create_playlist.side_effect = ["y1", "y2"]
        result = self.runner.invoke(
            cli, ["youtube", "push", "playlists"], catch_exceptions=False
        )

        expected_messages = (
            "Creating playlists",
            "Playlist: {}".format(p_one.display_type),
            "Playlist: {}".format(p_two.display_type),
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

    def test_playlists_empty_list(self):
        result = self.runner.invoke(
            cli, ["youtube", "push", "playlists"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertIn("There are no new playlists", result.output)

    @mock.patch.object(YouService, "remove_playlist_item")
    @mock.patch.object(YouService, "create_playlist_item")
    @mock.patch.object(YouService, "get_playlist_items")
    @mock.patch.object(TrackManager, "find")
    @mock.patch.object(PlaylistManager, "find")
    def test_tracks(
        self,
        find_playlists,
        find_tracks,
        get_playlist_items,
        create_playlist_item,
        remove_playlist_item,
    ):

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
            cli, ["youtube", "push", "tracks"], catch_exceptions=False
        )

        expected_output = (
            "Syncing playlists",
            "Fetching playlist items: Type A",
            "Adding new playlist items",
            "Adding video: $b",
            "Adding video: $c",
            "Removing playlist items",
            "Removing video: $e",
            "Fetching playlist items: Type B",
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
