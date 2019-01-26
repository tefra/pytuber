import click
from tabulate import tabulate

from pytuber.core import params
from pytuber.core.models import PlaylistManager


@click.command()
@click.option("--provider", type=params.ProviderParamType(), required=False)
def list(provider: str):
    """List playlists."""

    kwargs = dict(provider=provider) if provider else dict()
    playlists = PlaylistManager.find(**kwargs)

    if len(playlists) == 0:
        click.secho(
            'No playlists found, use "pytuber add" or '
            '"pytuber fetch youtube --playlists"'
        )
    else:
        click.secho(
            tabulate(  # type: ignore
                [
                    (
                        p.id,
                        p.title,
                        p.provider,
                        click.style("✔", fg="green") if p.youtube_id else "-",
                        len(p.tracks),
                    )
                    for p in playlists
                ],
                headers=("ID", "Title", "Provider", "Youtube", "Tracks"),
                colalign=("left", "left", "left", "center"),
            )
        )
