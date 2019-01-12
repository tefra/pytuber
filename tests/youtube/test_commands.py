from unittest import mock

from google.oauth2.credentials import Credentials

from pytuber import cli
from pytuber.models import (
    ConfigManager,
    Playlist,
    PlaylistManager,
    Provider,
    Track,
    TrackManager,
)
from pytuber.youtube.models import PlaylistItem
from pytuber.youtube.services import YouService
from tests.utils import CommandTestCase


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
        track_one = Track(artist="a", name="b")
        track_two = Track(artist="e", name="f")
        find.return_value = [track_one, track_two]

        search.side_effect = ["y1", "y3"]
        result = self.runner.invoke(
            cli, ["youtube", "fetch", "tracks"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertIn("Fetching tracks information", result.output)
        self.assertIn("Track: a - b", result.output)
        self.assertIn("Track: e - f", result.output)

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
        p_one = Playlist(id=1, type=None, provider=None, limit=10)
        p_two = Playlist(id=2, type=None, provider=None, limit=10)
        get_playlists.return_value = [p_one, p_two]

        result = self.runner.invoke(
            cli, ["youtube", "fetch", "playlists"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertIn("Fetching playlists information", result.output)
        self.assertIn("Imported playlist {}".format(p_one.id), result.output)
        self.assertIn("Imported playlist {}".format(p_two.id), result.output)

        get_playlists.assert_called_once_with()
        set_playlist.assert_has_calls(
            [mock.call(p_one.asdict()), mock.call(p_two.asdict())]
        )


class CommandGroupPushTests(CommandTestCase):
    @mock.patch.object(YouService, "create_playlist")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_playlists(self, find, update, create_playlist):
        p_one = Playlist(id=1, type="one", provider=None, limit=10)
        p_two = Playlist(id=2, type="two", provider=None, limit=10)
        find.return_value = [p_one, p_two]
        create_playlist.side_effect = ["y1", "y2"]
        result = self.runner.invoke(
            cli, ["youtube", "push", "playlists"], catch_exceptions=False
        )

        self.assertEqual(0, result.exit_code)
        self.assertIn("Creating playlists", result.output)
        self.assertIn("Playlist: {}".format(p_one.display_type), result.output)
        self.assertIn("Playlist: {}".format(p_two.display_type), result.output)

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
        tracks = {}
        for ltr in "abcdef":
            tracks[ltr] = Track(
                artist=ltr, name="@%s" % ltr, youtube_id="$%s" % ltr
            )

        p_one = Playlist(
            id=1, type="one", provider=None, limit=10, tracks=["a", "b", "c"]
        )
        p_two = Playlist(
            id=2, type="two", provider=None, limit=10, tracks=["d", "e", "f"]
        )
        find_playlists.return_value = [p_one, p_two]
        find_tracks.side_effect = [
            [tracks.get("a"), tracks.get("b"), tracks.get("c")],
            [tracks.get("d"), tracks.get("e"), tracks.get("f")],
        ]

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

        self.assertEqual(0, result.exit_code)
        get_playlist_items.assert_has_calls(
            [mock.call(p_one), mock.call(p_two)]
        )

        create_playlist_item.assert_has_calls(
            [
                mock.call(p_one, tracks.get("b").youtube_id),
                mock.call(p_one, tracks.get("c").youtube_id),
            ]
        )
        remove_playlist_item.assert_called_once_with(PlaylistItem(2, "$e"))

        expected_output = (
            "Syncing playlists",
            "Fetching playlist items: One",
            "Adding new playlist items",
            "Adding video: $b",
            "Adding video: $c",
            "Removing playlist items",
            "Removing video: $e",
            "Fetching playlist items: Two",
            "Playlist is already synced!",
        )

        for i, line in enumerate(result.output.strip().split("\n")):
            self.assertIn(expected_output[i], line)
