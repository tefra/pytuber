import os

import click
from click import Context

from pytubefm.lastfm.commands import lastfm
from pytubefm.models import Storage
from pytubefm.youtube.commands import youtube


@click.group()
@click.pass_context
def cli(ctx: Context):
    Storage.from_file(
        os.path.join(click.get_app_dir("pytubefm", False), "storage.db")
    )
    ctx.call_on_close(Storage.sync)


cli.add_command(youtube)
cli.add_command(lastfm)

if __name__ == "__main__":
    cli()
