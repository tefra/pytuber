import click

from pytubefm.lastfm.commands import lastfm
from pytubefm.youtube.commands import youtube


@click.group()
def cli():
    pass


cli.add_command(youtube)
cli.add_command(lastfm)

if __name__ == "__main__":
    cli()
