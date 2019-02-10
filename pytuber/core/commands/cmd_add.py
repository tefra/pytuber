from typing import List

import click
from tabulate import tabulate

from pytuber.core.models import (
    PlaylistManager,
    PlaylistType,
    Provider,
    TrackManager,
)
from pytuber.lastfm.commands.cmd_add import option_title
from pytuber.utils import magenta


@click.command("editor")
@option_title()
def editor(title: str) -> None:
    """Create playlists with a text editor."""
    click.clear()
    marker = (
        "\n\n# Copy/Paste your track list and hit save!\n"
        "# One line per track, make sure it doesn't start with a #\n"
        "# Separate the track artist and title with a single dash `-`\n"
    )
    message = click.edit(marker)
    if message is None:
        return click.secho("Aborted!")

    tracks: List[tuple] = []
    for line in message.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("-", 1)
        if len(parts) != 2:
            continue

        artist, track = list(map(str.strip, parts))
        if not artist or not track or (artist, track) in tracks:
            continue

        tracks.append((artist, track))

    click.secho(
        "{}\n\n{}\n".format(
            tabulate(  # type: ignore
                [
                    (magenta("Title:"), title),
                    (magenta("Tracks:"), len(tracks)),
                ],
                tablefmt="plain",
                colalign=("right", "left"),
            ),
            tabulate(  # type: ignore
                [
                    (i + 1, track[0], track[1])
                    for i, track in enumerate(tracks)
                ],
                headers=("No", "Artist", "Track Name"),
            ),
        )
    )
    click.confirm("Are you sure you want to save this playlist?", abort=True)
    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.EDITOR,
            provider=Provider.user,
            title=title.strip(),
            tracks=[
                TrackManager.set(dict(artist=artist, name=name)).id
                for artist, name in tracks
            ],
        )
    )
    click.secho("Added playlist: {}!".format(playlist.id))
