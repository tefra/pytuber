from datetime import timedelta

import click
from tabulate import tabulate

from pytuber.core.models import ConfigManager, Provider
from pytuber.core.services import YouService
from pytuber.utils import magenta


@click.command()
def quota():
    """Show current youtube calculated quota usage."""

    limit = ConfigManager.get(Provider.youtube).data["quota_limit"]
    usage = YouService.get_quota_usage()
    pt_date = YouService.quota_date(obj=True)
    next_reset = timedelta(
        hours=23 - pt_date.hour,
        minutes=59 - pt_date.minute,
        seconds=60 - pt_date.second,
    )

    values = [
        (magenta("Provider:"), Provider.youtube),
        (magenta("Limit:"), limit),
        (magenta("Usage:"), usage),
        (magenta("Next reset:"), str(next_reset)),
    ]

    click.secho(
        tabulate(  # type: ignore
            values, tablefmt="plain", colalign=("right", "left")
        )
    )
