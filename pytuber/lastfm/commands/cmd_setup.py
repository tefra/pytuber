import click

from pytuber.core.models import ConfigManager, Provider


@click.command("lastfm")
@click.option(
    "--api-key", help="Your last.fm api key", prompt="Last.fm Api Key"
)
def setup(api_key: str) -> None:
    """
    Configure your last.fm api account.

    Signup for a last.fm api account and use your api key in order to
    use last.fm as a playlists source for pytuber.
    """

    if ConfigManager.get(Provider.lastfm, default=None):
        click.confirm("Overwrite existing configuration?", abort=True)

    ConfigManager.set(
        dict(provider=Provider.lastfm.value, data=dict(api_key=api_key))
    )
    click.secho("Last.fm configuration updated!")
