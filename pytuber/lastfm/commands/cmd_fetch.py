from typing import List

import click
from tabulate import tabulate

from pytuber.core.models import PlaylistManager, Provider, TrackManager
from pytuber.lastfm.services import LastService
from pytuber.utils import spinner


@click.command("lastfm")
@click.option("--tracks", is_flag=True, help="Update the playlist tracks")
@click.option("--tags", is_flag=True, help="Show the most popular tags")
@click.pass_context
def fetch(ctx: click.Context, tracks: bool = False, tags: bool = False):
    """Fetch tracks and tags information from last.fm."""

    if tracks == tags:
        click.secho(ctx.get_help())
        click.Abort()

    if tracks:
        fetch_tracks()
    elif tags:
        fetch_tags()


def fetch_tracks(*args):
    kwargs = dict(provider=Provider.lastfm)
    if args:
        kwargs["id"] = lambda x: x in args

    # So wrong, but yaspin doesn't support nested spinners
    LastService.get_tags()
    with spinner("Fetching track lists") as sp:
        for playlist in PlaylistManager.find(**kwargs):
            tracklist = LastService.get_tracks(
                type=playlist.type, **playlist.arguments
            )

            track_ids: List[str] = []
            for entry in tracklist:
                id = TrackManager.set(
                    dict(artist=entry.artist.name, name=entry.name)
                ).id

                if id not in track_ids:
                    track_ids.append(id)

            sp.write(
                "Playlist: {} - {} tracks".format(playlist.id, len(track_ids))
            )
            PlaylistManager.update(playlist, dict(tracks=track_ids))


def fetch_tags():
    values = [
        (tag.name, tag.count, tag.reach) for tag in LastService.get_tags()
    ]

    click.echo_via_pager(
        tabulate(
            values,
            showindex="always",
            headers=("No", "Name", "Count", "Reach"),
        )
    )
