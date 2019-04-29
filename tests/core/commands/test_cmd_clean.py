from pytuber import cli
from pytuber.core.models import PlaylistManager, TrackManager
from tests.utils import CommandTestCase, PlaylistFixture, TrackFixture


class CommandCleanTests(CommandTestCase):
    def test_removes_orphan_tracks_and_empty_playlists(self):
        for fixture in TrackFixture.get(2):
            TrackManager.save(fixture.asdict())

        for fixture in PlaylistFixture.get(3):
            PlaylistManager.save(fixture.asdict())

        playlist = PlaylistFixture.one(num=50)
        track = TrackFixture.one(num=5)
        playlist.tracks = [track.id]
        PlaylistManager.save(playlist.asdict())
        TrackManager.save(track.asdict())

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
