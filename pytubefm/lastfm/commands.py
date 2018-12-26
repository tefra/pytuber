import click

import pytubefm
from pytubefm.main import Context, pass_context


@click.group("lastfm")
def lastfm():
    pass


@lastfm.command()
@click.option(
    "--api-key", help="Your last.fm api key", prompt="Last.fm Api Key"
)
@pass_context
def setup(ctx: Context, api_key: str) -> None:
    """
    Configure your last.fm api account.

    Signup for a last.fm api account and use your api key in order to use
    last.fm as a playlists source for pytubefm.

    \f
    :param ctx: pytube context class
    :type ctx: :class:`pytubefm.main.Context`
    :param str api_key: Your api key
    """

    if ctx.get_config(pytubefm.LASTFM):
        click.confirm("Overwrite existing configuration?", abort=True)

    ctx.update_config(pytubefm.LASTFM, dict(api_key=api_key))
    click.secho("Last.fm configuration updated!")
