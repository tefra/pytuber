import click

from pytubefm.models import Config, Provider


@click.group("lastfm")
def lastfm():
    pass


@lastfm.command()
@click.option(
    "--api-key", help="Your last.fm api key", prompt="Last.fm Api Key"
)
def setup(api_key: str) -> None:
    """
    Configure your last.fm api account.

    Signup for a last.fm api account and use your api key in order to use
    last.fm as a playlists source for pytubefm.

    \f
    :param str api_key: Your api key
    """

    if Config.find_by_provider(Provider.lastfm):
        click.confirm("Overwrite existing configuration?", abort=True)

    Config(provider=Provider.lastfm.value, data=dict(api_key=api_key)).save()
    click.secho("Last.fm configuration updated!")
