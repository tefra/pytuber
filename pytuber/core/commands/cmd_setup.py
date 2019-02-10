import click

from pytuber.core.models import ConfigManager, Provider
from pytuber.core.services import YouService


@click.command("youtube")
@click.argument("client-secrets", type=click.Path(), required=True)
@click.option(
    "--quota-limit",
    "--q",
    type=click.INT,
    required=False,
    default=1000000,
    help="Override default youtube quota limit",
)
def setup(client_secrets: str, quota_limit: int) -> None:
    """
    Configure your youtube api credentials.

    Create a project in the Google Developers Console and obtain
    authorization credentials so pytuber can submit API requests.
    Download your `config_secret.json` and pass the path as an argument
    to this method
    """

    if ConfigManager.get(Provider.youtube, default=None):
        click.confirm("Overwrite existing configuration?", abort=True)

    credentials = YouService.authorize(client_secrets)
    ConfigManager.set(
        dict(
            provider=Provider.youtube.value,
            data=dict(
                refresh_token=credentials.refresh_token,
                token_uri=credentials.token_uri,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                scopes=credentials.scopes,
                quota_limit=quota_limit,
            ),
        )
    )
    click.secho("Youtube configuration updated!")
