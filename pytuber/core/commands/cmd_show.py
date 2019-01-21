from typing import Optional

import click
from tabulate import tabulate

from pytuber.models import PlaylistManager, TrackManager


@click.command("show")
@click.argument("id", required=False)
def show_playlist(id: Optional[str]):
    """Show a playlist track list."""

    playlist = PlaylistManager.get(id)
    click.echo_via_pager(
        tabulate(
            [
                (t.artist, t.name, "✔" if t.youtube_id else "-")
                for t in [TrackManager.get(id) for id in playlist.tracks]
            ],
            showindex=True,
            headers=("No", "Artist", "Track Name", "Youtube"),
        )
    )
