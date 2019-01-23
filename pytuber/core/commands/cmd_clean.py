import click

from pytuber.core.models import PlaylistManager, TrackManager


@click.command("clean")
def clean():
    """Cleanup youtube related data from playlists and tracks."""

    for playlist in PlaylistManager.find():
        if playlist.youtube_id:
            PlaylistManager.update(playlist, dict(youtube_id=None))

    for track in TrackManager.find():
        if track.youtube_id:
            TrackManager.update(track, dict(youtube_id=None))
