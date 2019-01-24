import click

from pytuber.core.models import PlaylistManager, TrackManager
from pytuber.core.services import YouService
from pytuber.utils import spinner


@click.command("youtube")
@click.option("--all", is_flag=True, help="Perform all tasks")
@click.option("--playlists", is_flag=True, help="Create new playlists")
@click.option("--tracks", is_flag=True, help="Update playlist items")
@click.pass_context
def fetch(
    ctx: click.Context,
    tracks: bool = False,
    playlists: bool = False,
    all: bool = False,
):
    """Fetch youtube online playlist and tracks data."""

    if not all and not playlists and not tracks:
        click.secho(ctx.get_help())
        click.Abort()

    if all or playlists:
        fetch_playlists()
    if all or tracks:
        fetch_tracks()


def fetch_playlists():
    message = "Fetching playlists information"
    with spinner(message) as sp:
        playlists = YouService.get_playlists()
        for playlist in playlists:
            PlaylistManager.set(playlist.asdict())

        total = len(playlists)
        if total > 0:
            sp.text = "{0}: {1}/{1} ".format(message, total)


def fetch_tracks():
    tracks = TrackManager.find(youtube_id=None)
    message = "Searching tracks videos"
    with spinner(message) as sp:
        for track in tracks:
            sp.text = "{}: {} - {}".format(message, track.artist, track.name)
            youtube_id = YouService.search_track(track)
            TrackManager.update(track, dict(youtube_id=youtube_id))

        total = len(tracks)
        if total > 0:
            sp.text = "{0}: {1}/{1} ".format(message, total)
