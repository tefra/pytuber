import json
from typing import TextIO

import click

import pytubefm
from pytubefm.main import Context, pass_context


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
@pass_context
def setup(ctx: Context, credentials: TextIO) -> None:
    """
    Configure your youtube api credentials.

    Create a project in the Google Developers Console and obtain authorization
    credentials so pytubefm can submit API requests. Download your
    `config_secret.json` and pass the path as an argument to this method

    \f
    :param ctx: pytube context class
    :type ctx: :class:`pytubefm.main.Context`
    :param credentials: The path where you downloaded your youtube client secret file
    :type credentials: :class:`io.TextIOWrapper`
    """

    if ctx.get_config(pytubefm.YOUTUBE):
        click.confirm("Overwrite existing configuration?", abort=True)

    ctx.update_config(pytubefm.YOUTUBE, json.load(credentials))
    click.secho("Youtube configuration updated!")
