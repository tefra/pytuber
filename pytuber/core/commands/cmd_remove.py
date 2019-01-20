from typing import Tuple

import click

from pytuber.models import PlaylistManager


@click.command("remove")
@click.argument("ids", required=True, nargs=-1)
def remove_playlists(ids: Tuple[str]):
    """Remove one or more playlists by id."""

    click.confirm("Do you want to continue?", abort=True)
    for id in ids:
        PlaylistManager.remove(id)
        click.secho("Removed playlist: {}!".format(id))
