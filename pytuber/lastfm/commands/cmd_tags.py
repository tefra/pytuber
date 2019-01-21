import click
from tabulate import tabulate

from pytuber.lastfm.services import LastService


@click.command()
@click.option("--refresh", help="Refresh cache", is_flag=True, default=False)
def tags(refresh: bool):
    """Show a list of the most popular user tags from last.fm."""
    values = [
        (tag.name, tag.count, tag.reach)
        for tag in LastService.get_tags(refresh=refresh)
    ]

    click.echo_via_pager(
        tabulate(
            values, showindex=True, headers=("No", "Name", "Count", "Reach")
        )
    )
