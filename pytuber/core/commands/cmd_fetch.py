import click

from pytuber.core.services import YouService
from pytuber.models import PlaylistManager, TrackManager
from pytuber.utils import spinner


@click.group("youtube", invoke_without_command=True)
@click.option("--all", is_flag=True, default=False, help="Fetch everything")
@click.pass_context
def fetch(ctx: click.Context, all=False):
    """Fetch information from youtube."""
    if ctx.invoked_subcommand is None:
        if all:
            ctx.invoke(fetch_playlists)
            ctx.invoke(fetch_tracks)
        else:
            click.secho(ctx.get_help())
            click.Abort()


@fetch.command("playlists")
def fetch_playlists():
    """Fetch remote information and update local playlists."""
    with spinner("Fetching playlists information") as sp:
        for playlist in YouService.get_playlists():
            exists = PlaylistManager.exists(playlist)
            PlaylistManager.set(playlist.asdict())
            sp.write(
                "{} playlist {}".format(
                    "Updated" if exists else "Imported", playlist.id
                )
            )


@fetch.command("tracks")
def fetch_tracks():
    """Match local tracks to youtube videos."""

    tracks = TrackManager.find(youtube_id=None)
    if len(tracks) == 0:
        return click.secho("There are no new tracks")

    click.secho("Fetching tracks information", bold=True)
    for track in tracks:
        with spinner("Track: {} - {}".format(track.artist, track.name)):
            youtube_id = YouService.search_track(track)
            TrackManager.update(track, dict(youtube_id=youtube_id))
