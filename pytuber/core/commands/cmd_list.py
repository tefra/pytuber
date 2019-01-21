import click
from tabulate import tabulate

from pytuber.models import PlaylistManager
from pytuber.utils import date


@click.command("list")
@click.option("--provider", required=False)
def list_playlists(provider: str):
    """List all playlists, filtered by provider optionally."""

    kwargs = dict(provider=provider) if provider else dict()
    click.secho(
        tabulate(
            [
                (
                    p.id,
                    p.provider,
                    "✔" if p.youtube_id else "-",
                    p.display_type,
                    p.display_arguments,
                    date(p.modified),
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
                "Modified",
                "Synced",
                "Uploaded",
            ),
        )
    )
