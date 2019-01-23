import click
import click_completion

from pytuber.core.services import YouService
from pytuber.models import ConfigManager, Provider


@click.command("youtube")
@click.argument("client-secrets", type=click.Path(), required=True)
def setup(client_secrets: str) -> None:
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
            ),
        )
    )
    click.secho("Youtube configuration updated!")


@click.command()
@click.option(
    "--append/--overwrite",
    help="Append the completion code to the file",
    default=None,
)
@click.option(
    "-i",
    "--case-insensitive/--no-case-insensitive",
    help="Case insensitive completion",
)
@click.argument(
    "shell",
    required=False,
    type=click_completion.DocumentedChoice(click_completion.core.shells),
)
@click.argument("path", required=False)
def autocomplete(append, case_insensitive, shell, path):
    """Install the click-completion-command completion."""
    extra_env = (
        {"_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE": "ON"}
        if case_insensitive
        else {}
    )
    shell, path = click_completion.core.install(
        shell=shell, path=path, append=append, extra_env=extra_env
    )
    click.echo("%s completion installed in %s" % (shell, path))
