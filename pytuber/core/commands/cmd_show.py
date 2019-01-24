from functools import partial
from typing import Optional

import click
from tabulate import tabulate

from pytuber.core import params
from pytuber.core.models import PlaylistManager, TrackManager
from pytuber.utils import date


@click.command()
@click.argument("id", type=params.PlaylistParamType())
def show(id: Optional[str]):
    """Show a playlist track list."""

    playlist = PlaylistManager.get(id)
    magenta = partial(click.style, fg="magenta")
    info = tabulate(  # type: ignore
        [
            (magenta("ID:"), playlist.id),
            (magenta("Provider:"), playlist.provider),
            (magenta("Title:"), playlist.title),
            (magenta("Type:"), playlist.type),
            (magenta("Arguments:"), playlist.display_arguments),
            (magenta("Synced:"), date(playlist.synced)),
            (magenta("Uploaded:"), date(playlist.uploaded)),
            (magenta("Youtube:"), playlist.youtube_url),
            (magenta("Tracks:"),),
        ],
        tablefmt="plain",
        colalign=("right", "left"),
    )

    tracks = tabulate(  # type: ignore
        [
            (
                t.artist,
                t.name,
                click.style("✔", fg="green") if t.youtube_id else "-",
            )
            for t in [TrackManager.get(id) for id in playlist.tracks]
        ],
        showindex="always",
        headers=("No", "Artist", "Track Name", "Youtube"),
        colalign=("left", "left", "left", "center"),
    )

    click.echo_via_pager("{}\n\n{}".format(info, tracks))
