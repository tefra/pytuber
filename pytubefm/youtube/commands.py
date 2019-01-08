import json
from typing import TextIO

import click
from google_auth_oauthlib.flow import InstalledAppFlow

from pytubefm.models import ConfigManager, Provider, TrackManager
from pytubefm.youtube.models import SCOPES
from pytubefm.youtube.services import YouService


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
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
            },
        )
    )
    click.secho("Youtube configuration updated!")

    """Sync online/offline data"""


@youtube.command()
def match():
    """Match local tracks to youtube videos."""

    tracks = [track for track in TrackManager.find() if not track.youtube_id]
    with click.progressbar(tracks, label="Matching tracks") as track_list:
        for track in track_list:
            youtube_id = YouService.search(track)
            if youtube_id:
                TrackManager.update(track, dict(youtube_id=youtube_id))


@youtube.command()
def push():
    pass
