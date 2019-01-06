import os

import click
from click import Context

from pytubefm.lastfm.commands import lastfm
from pytubefm.storage import Registry
from pytubefm.youtube.commands import youtube


@click.group()
@click.pass_context
def cli(ctx: Context):
    cfg = os.path.join(click.get_app_dir("pytubefm", False), "storage.db")

    Registry.from_file(cfg)
    ctx.call_on_close(lambda: Registry.persist(cfg))


cli.add_command(youtube)
cli.add_command(lastfm)

if __name__ == "__main__":
    cli()
