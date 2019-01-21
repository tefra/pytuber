import os

import click

from pytuber.core import commands as core
from pytuber.lastfm import commands as lastfm
from pytuber.storage import Registry


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """
    Create and upload youtube playlists from various sources like last.fm.

    Usage Example:

    $ pytuber add lastfm tag-playlist

    $ pytuber fetch youtube --all

    $ pytuber push youtube --all
    """
    cfg = os.path.join(click.get_app_dir("pytuber", False), "storage.db")

    Registry.from_file(cfg)
    ctx.call_on_close(lambda: Registry.persist(cfg))


cli.add_command(core.list_playlists)
cli.add_command(core.show_playlist)
cli.add_command(core.remove_playlists)
cli.add_command(lastfm.tags)


@cli.group()
def setup():
    """Configure api keys and credentials."""


setup.add_command(lastfm.setup)
setup.add_command(core.setup)


@cli.group()
def add():
    """Add playlist."""


add.add_command(lastfm.add_playlist)


@cli.group()
def fetch():
    """Retrieve playlist or track info."""


fetch.add_command(lastfm.fetch_playlists)
fetch.add_command(core.fetch)


@cli.group()
def push():
    """Update playlists and tracks."""


push.add_command(core.push)

if __name__ == "__main__":
    cli()
