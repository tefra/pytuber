from typing import Optional

import click
from tabulate import tabulate

from pytuber.core import params
from pytuber.core.models import PlaylistManager, TrackManager
from pytuber.utils import date, magenta


@click.command()
@click.argument("id", type=params.PlaylistParamType())
@click.option("--mime", is_flag=True, help="How to push the playlist manually")
def show(id: Optional[str], mime: bool = False):
    """Show a playlist track list."""

    playlist = PlaylistManager.get(id)
    values = [
        (magenta("ID:"), playlist.id),
        (magenta("Provider:"), playlist.provider),
        (magenta("Title:"), playlist.title),
        (magenta("Type:"), playlist.type),
        (magenta("Arguments:"), playlist.display_arguments),
        (magenta("Synced:"), date(playlist.synced)),
        (magenta("Uploaded:"), date(playlist.uploaded)),
        (magenta("Youtube:"), playlist.youtube_url),
    ]

    if mime:
        values.append((magenta("Mime:"), playlist.mime))
    else:
        values.append((magenta("Tracks:"), ""))

    info = tabulate(  # type: ignore
        values, tablefmt="plain", colalign=("right", "left")
    )

    if mime:
        click.secho(info)
        click.secho("\nYou reached the 10 playlists limit per day on youtube?")
        click.secho(
            "Create a playlist manually and add "
            "in the bottom the above mime string"
        )
        click.secho(
            "The mime is base64 signature that "
            "pytuber uses to link with youtube playlists"
        )
        click.secho(
            'Use "pytuber fetch youtube --playlists"'
            " to sync, before you try to push any tracks"
        )
        return

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
