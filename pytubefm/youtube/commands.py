import json
from typing import TextIO

import click
from google_auth_oauthlib.flow import InstalledAppFlow

from pytubefm.models import ConfigManager, Provider
from pytubefm.youtube.models import SCOPES


@click.group("youtube")
def youtube():
    pass


@youtube.command()
@click.argument("client-secrets", type=click.File(), required=True)
def setup(client_secrets: TextIO) -> None:
    """
    Configure your youtube api credentials.

    Create a project in the Google Developers Console and obtain
    authorization credentials so pytubefm can submit API requests.
    Download your `config_secret.json` and pass the path as an argument
    to this method
    """

    if ConfigManager.get(Provider.youtube):
        click.confirm("Overwrite existing configuration?", abort=True)

    flow = InstalledAppFlow.from_client_config(
        json.load(client_secrets), scopes=SCOPES
    )
    creds = flow.run_console()

    ConfigManager.update(
        dict(
            provider=Provider.youtube.value,
            data={
                # 'token': creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
            },
        )
    )
    click.secho("Youtube configuration updated!")
