import click
from tabulate import tabulate

from pytuber.lastfm.services import LastService


@click.command()
@click.option("--refresh", help="Refresh cache", is_flag=True)
def tags(refresh: bool = False):
    """Show a list of the most popular user tags from last.fm."""
    values = [
        (tag.name, tag.count, tag.reach)
        for tag in LastService.get_tags(refresh=refresh)
    ]

    click.echo_via_pager(
        tabulate(
            values,
            showindex="always",
            headers=("No", "Name", "Count", "Reach"),
        )
    )
