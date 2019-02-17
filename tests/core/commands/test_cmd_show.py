from unittest import mock

from pytuber import cli
from pytuber.core.models import PlaylistManager, TrackManager
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandShowPlaylistsTests(CommandTestCase):
    @mock.patch.object(TrackManager, "get")
    @mock.patch.object(PlaylistManager, "get")
    def test_show_playlist(self, get_playlist, get_track):
        playlist = PlaylistFixture.one(tracks=[1, 2, 3])

        get_playlist.return_value = playlist
        get_track.side_effect = TrackFixture.get(3, youtube_id=[None, "a", ""])

        result = self.runner.invoke(cli, ["show", playlist.id])

        expected_output = (
            "ID:  id_a",
            " Provider:  provider_a",
            "    Title:  title_a",
            "     Type:  type_a",
            "Arguments:  a: 0",
            "   Synced:  -",
            " Uploaded:  -",
            "  Youtube:  -",
            "   Tracks:",
            "",
            "No    Artist    Track Name     Youtube",
            "----  --------  ------------  ---------",
            "0     artist_a  name_a            -",
            "1     artist_b  name_b            ✔",
            "2     artist_c  name_c            -",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        get_playlist.assert_called_once_with(playlist.id)
        get_track.assert_has_calls([mock.call(id) for id in playlist.tracks])

    @mock.patch.object(PlaylistManager, "get")
    def test_show_playlist_mime(self, get_playlist):
        playlist = PlaylistFixture.one(tracks=[1, 2, 3])

        get_playlist.return_value = playlist
        result = self.runner.invoke(cli, ["show", playlist.id, "--mime"])

        expected_output = (
            "ID:  id_a",
            " Provider:  provider_a",
            "    Title:  title_a",
            "     Type:  type_a",
            "Arguments:  a: 0",
            "   Synced:  -",
            " Uploaded:  -",
            "  Youtube:  -",
            "     Mime:  eyJhcmd1bWVudHMiOiB7ImEiOiAwfSwgInByb3ZpZGVyIjogInByb3ZpZGVyX2EiLCAidHlwZSI6ICJ0eXBlX2EiLCAidGl0bGUiOiAidGl0bGVfYSJ9",
            "",
            "You reached the 10 playlists limit per day on youtube?",
            "Create a playlist manually and add in the bottom the above mime string",
            "The mime is base64 signature that pytuber uses to link with youtube playlists",
            'Use "pytuber fetch youtube --playlists" to sync, before you try to push any tracks',
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        get_playlist.assert_called_once_with(playlist.id)
