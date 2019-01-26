import os

import click
import click_completion

from pytuber.core import commands as core
from pytuber.lastfm import commands as lastfm
from pytuber.storage import Registry

click_completion.init(complete_options=True)


@click.group(
    help="""\b
Create and upload youtube playlists from various sources like last.fm.
\b
Usage Example:
\b
On a fresh install configure youtube and any other 3rd party providers
 $ pytuber setup lastfm|youtube
\b
If you have pytuber playlists uploaded on youtube but not your local
 $ pytuber fetch youtube --playlist
\b
Update the track lists from the original provider
 $ pytuber fetch lastfm
\b
Create a new playlist
 $ pytuber add lastfm tag-playlist
\b
Match any new tracks with youtube videos
 $ pytuber fetch youtube --tracks
\b
Push your updates to youtube
 $ pytuber push youtube --all
 """
)
@click.pass_context
def cli(ctx: click.Context):
    cfg = os.path.join(click.get_app_dir("pytuber", False), "storage.db")

    Registry.from_file(cfg)
    ctx.call_on_close(lambda: Registry.persist(cfg))
    click.secho("")


cli.add_command(core.list)
cli.add_command(core.show)
cli.add_command(core.remove)
cli.add_command(core.clean)


@cli.group()
def setup():
    """Configure api keys and credentials."""


setup.add_command(lastfm.setup)
setup.add_command(core.setup)
setup.add_command(core.autocomplete)


@cli.group()
def add():
    """Add playlist."""


add.add_command(lastfm.add)


@cli.group()
def fetch():
    """Retrieve playlist or track info."""


fetch.add_command(lastfm.fetch)
fetch.add_command(core.fetch)


@cli.group()
def push():
    """Update playlists and tracks."""


push.add_command(core.push)

if __name__ == "__main__":
    cli()
