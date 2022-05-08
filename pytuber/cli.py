import os

import click
import click_completion

from pytuber import __version__
from pytuber.core import commands as core
from pytuber.lastfm import commands as lastfm
from pytuber.storage import Registry
from pytuber.utils import init_registry

click_completion.init(complete_options=True)


@click.group()
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context):
    """Create and upload music playlists to youtube."""
    appdir = click.get_app_dir("pytuber", False)
    if not os.path.exists(appdir):
        print("Application Directory not found! Creating one at", appdir)
        os.makedirs(appdir)
    cfg = os.path.join(appdir, "storage.db")
    init_registry(cfg, __version__)

    ctx.call_on_close(lambda: Registry.persist(cfg))


cli.add_command(core.list)
cli.add_command(core.show)
cli.add_command(core.remove)
cli.add_command(core.clean)
cli.add_command(core.quota)


@cli.group()
def setup():
    """Configure api keys and credentials."""


setup.add_command(lastfm.setup)
setup.add_command(core.setup)
setup.add_command(core.autocomplete)


@cli.group()
def add():
    """Add playlist."""


add.add_command(core.add_from_editor)
add.add_command(core.add_from_file)
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
