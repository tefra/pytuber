from pytuber import cli
from pytuber.core.models import PlaylistManager, TrackManager
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandCleanTests(CommandTestCase):
    def test_removes_orphan_tracks_and_empty_playlists(self):
        [TrackManager.set(t.asdict()) for t in TrackFixture.get(2)]
        [PlaylistManager.set(p.asdict()) for p in PlaylistFixture.get(3)]

        playlist = PlaylistFixture.one(num=50)
        track = TrackFixture.one(num=5)
        playlist.tracks = [track.id]
        PlaylistManager.set(playlist.asdict())
        TrackManager.set(track.asdict())

        result = self.runner.invoke(cli, ["clean"])

        expected_output = (
            "Cleanup removed:",
            "   Tracks:  2",
            "Playlists:  3",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)

        self.assertEqual(track.id, TrackManager.find()[0].id)
        self.assertEqual(playlist.id, PlaylistManager.find()[0].id)
