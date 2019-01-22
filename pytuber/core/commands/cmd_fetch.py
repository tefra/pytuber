import click

from pytuber.core.services import YouService
from pytuber.models import PlaylistManager, TrackManager
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
    with spinner("Fetching playlists information") as sp:
        for playlist in YouService.get_playlists():
            exists = PlaylistManager.exists(playlist)
            PlaylistManager.set(playlist.asdict())
            sp.write(
                "{} playlist {}".format(
                    "Updated" if exists else "Imported", playlist.id
                )
            )


def fetch_tracks():
    tracks = TrackManager.find(youtube_id=None)
    if len(tracks) == 0:
        return click.secho("There are no new tracks")

    click.secho("Fetching tracks information", bold=True)
    for track in tracks:
        with spinner("Track: {} - {}".format(track.artist, track.name)):
            youtube_id = YouService.search_track(track)
            TrackManager.update(track, dict(youtube_id=youtube_id))
