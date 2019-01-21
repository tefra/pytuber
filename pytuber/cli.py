import os

import click
from click import Context

from pytuber.core.commands.cmd_fetch import youtube_fetch
from pytuber.core.commands.cmd_list import list_playlists
from pytuber.core.commands.cmd_push import youtube_push
from pytuber.core.commands.cmd_remove import remove_playlists
from pytuber.core.commands.cmd_setup import setup_youtube
from pytuber.core.commands.cmd_show import show_playlist
from pytuber.lastfm.commands.cmd_add import lastfm_playlist
from pytuber.lastfm.commands.cmd_fetch import lastfm_fetch
from pytuber.lastfm.commands.cmd_setup import setup_lastfm
from pytuber.lastfm.commands.cmd_tags import tags
from pytuber.storage import Registry


@click.group()
@click.pass_context
def cli(ctx: Context):
    """Create and upload youtube playlists from various sources like
    last.fm."""
    cfg = os.path.join(click.get_app_dir("pytuber", False), "storage.db")

    Registry.from_file(cfg)
    ctx.call_on_close(lambda: Registry.persist(cfg))


@cli.group()
def setup():
    """Setup providers api keys and credentials."""


@cli.group()
def add():
    """Add provider playlists."""


@cli.group()
def fetch():
    """Fetch provider playlist information."""


@cli.group()
def push():
    """Push playlists to youtube."""


push.add_command(youtube_push)
fetch.add_command(lastfm_fetch)
fetch.add_command(youtube_fetch)
setup.add_command(setup_lastfm)
setup.add_command(setup_youtube)
add.add_command(lastfm_playlist)

cli.add_command(list_playlists)
cli.add_command(show_playlist)
cli.add_command(remove_playlists)
cli.add_command(tags)


if __name__ == "__main__":
    cli()
