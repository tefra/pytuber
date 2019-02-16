import click
from tabulate import tabulate

from pytuber.core.models import PlaylistManager, TrackManager
from pytuber.utils import magenta


@click.command("clean")
def clean():
    """Cleanup orphan tracks and empty playlists."""

    tracks = []
    removed_playlists = 0
    for playlist in PlaylistManager.find():

        if len(playlist.tracks) == 0:
            PlaylistManager.remove(playlist.id)
            removed_playlists += 1
        else:
            tracks += playlist.tracks

    tracks = list(set(tracks))
    removed_tracks = 0
    for track in TrackManager.find():
        if track.id not in tracks:
            TrackManager.remove(track.id)
            removed_tracks += 1

    click.secho("Cleanup removed:", bold=True)
    click.secho(
        tabulate(  # type: ignore
            [
                (magenta("Tracks:"), removed_tracks),
                (magenta("Playlists:"), removed_playlists),
            ],
            tablefmt="plain",
            colalign=("right", "left"),
        )
    )
