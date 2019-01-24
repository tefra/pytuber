import click
from tabulate import tabulate

from pytuber.core import params
from pytuber.core.models import PlaylistManager
from pytuber.utils import date


@click.command()
@click.option("--provider", type=params.ProviderParamType(), required=False)
def list(provider: str):
    """List all playlists, filtered by provider optionally."""

    kwargs = dict(provider=provider) if provider else dict()
    click.secho(
        tabulate(
            [
                (
                    p.id,
                    p.provider,
                    "✔" if p.youtube_id else "-",
                    p.title,
                    p.display_arguments,
                    date(p.synced),
                    date(p.uploaded),
                )
                for p in PlaylistManager.find(**kwargs)
            ],
            headers=(
                "ID",
                "Provider",
                "Youtube",
                "Title",
                "Arguments",
                "Synced",
                "Uploaded",
            ),
        )
    )
