import json
from typing import TextIO

import click

from pytubefm.models import ConfigManager, Provider


@click.group("youtube")
def youtube():
    pass


@youtube.command()
@click.option(
    "--credentials",
    type=click.File(),
    help=(
        "The path of your youtube client secret file,"
        "eg: ~/Downloads/client_secret.json"
    ),
    prompt="Credentials file path",
)
def setup(credentials: TextIO) -> None:
    """
    Configure your youtube api credentials.

    Create a project in the Google Developers Console and obtain authorization
    credentials so pytubefm can submit API requests. Download your
    `config_secret.json` and pass the path as an argument to this method

    \f
    :param credentials: The path where you downloaded your youtube client secret file
    :type credentials: :class:`io.TextIOWrapper`
    """

    if ConfigManager.get(Provider.youtube):
        click.confirm("Overwrite existing configuration?", abort=True)

    ConfigManager.update(
        dict(provider=Provider.youtube.value, data=json.load(credentials))
    )
    click.secho("Youtube configuration updated!")
