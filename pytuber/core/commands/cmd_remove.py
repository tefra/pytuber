from typing import Tuple

import click

from pytuber.core import params
from pytuber.core.models import PlaylistManager


@click.command()
@click.argument(
    "ids", type=params.PlaylistParamType(), required=True, nargs=-1
)
def remove(ids: Tuple[str]):
    """Delete one or more playlists by id."""

    click.confirm("Do you want to continue?", abort=True)
    for id in ids:
        PlaylistManager.remove(id)
        click.secho("Removed playlist: {}!".format(id))
