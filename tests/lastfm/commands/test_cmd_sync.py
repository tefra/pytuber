from unittest import mock

import pydrag

from pytuber import cli
from pytuber.lastfm.services import LastService
from pytuber.models import PlaylistManager, Provider, TrackManager
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandSyncTests(CommandTestCase):
    @mock.patch.object(TrackManager, "set")
    @mock.patch.object(LastService, "get_tracks")
    @mock.patch.object(PlaylistManager, "update")
    @mock.patch.object(PlaylistManager, "find")
    def test_sync_playlists(self, find, update, get_tracks, set):

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

        result = self.runner.invoke(cli, ["sync", "lastfm", "playlists"])

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
            cli, ["sync", "lastfm", "playlists", playlists[1].id]
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
