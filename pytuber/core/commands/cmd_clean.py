import click

from pytuber.core.models import PlaylistManager, TrackManager


@click.command("clean")
def clean():
    """Cleanup youtube related data from playlists and tracks."""

    playlists = tracks = 0
    for playlist in PlaylistManager.find():
        if playlist.youtube_id:
            playlists += 1
            PlaylistManager.update(playlist, dict(youtube_id=None))

    for track in TrackManager.find():
        if track.youtube_id:
            tracks += 1
            TrackManager.update(track, dict(youtube_id=None))

    click.secho(
        "Removed youtube references from {} playlists and {} tracks".format(
            playlists, tracks
        )
    )
