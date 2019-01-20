import os

import click
from click import Context

from pytuber.core.commands import (
    list_playlists,
    remove_playlists,
    show_playlist,
)
from pytuber.lastfm.commands import lastfm
from pytuber.storage import Registry
from pytuber.youtube.commands import youtube


@click.group()
@click.pass_context
def cli(ctx: Context):
    """Create and upload youtube playlists from various sources like
    last.fm."""
    cfg = os.path.join(click.get_app_dir("pytuber", False), "storage.db")

    Registry.from_file(cfg)
    ctx.call_on_close(lambda: Registry.persist(cfg))


cli.add_command(list_playlists)
cli.add_command(show_playlist)
cli.add_command(remove_playlists)


cli.add_command(youtube)
cli.add_command(lastfm)

if __name__ == "__main__":
    cli()
