import click
from pydrag import Artist, Tag
from tabulate import tabulate

from pytubefm.exceptions import RecordExists
from pytubefm.lastfm.models import ChartPlaylist, UserPlaylist
from pytubefm.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
)
from pytubefm.lastfm.services import LastService
from pytubefm.models import Config, Playlist, Provider


@click.group()
def lastfm():
    pass


@lastfm.group()
def add():
    """Created or update a playlist."""


def create_or_update_playlist(playlist: Playlist):
    try:
        exists = False
        playlist.save()
    except RecordExists:
        exists = click.confirm("Overwrite existing playlist?", abort=True)
        playlist.save(overwrite=True)
    click.secho(
        "{} playlist: {}!".format(
            "Updated" if exists else "Added", playlist.id
        )
    )


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


@lastfm.command()
@click.option("--refresh", help="Refresh cache", is_flag=True, default=False)
def tags(refresh) -> None:
    values = [
        (tag.name, tag.count, tag.reach)
        for tag in LastService.get_tags(refresh=refresh)
    ]

    click.echo_via_pager(
        tabulate(
            values, showindex=True, headers=("No", "Name", "Count", "Reach")
        )
    )


@add.command("user")
@click.option(
    "--username",
    help="The user for whom the playlist will be generated",
    prompt="Last.fm username",
)
@click.option(
    "--playlist-type",
    help="The playlist type number",
    type=UserPlaylist.range(),
    prompt=UserPlaylist.choices(),
)
@click.option(
    "--limit",
    help="The maximum number of tracks",
    type=click.IntRange(50, 1000),
    prompt="Maximum tracks",
    default=50,
)
def add_user_playlist(username: str, playlist_type: int, limit: int):
    """
    Add a user type playlist. This type of playlists are based on a user's
    music preference and history.

    \b
    Playlist types:
    1. User loved tracks
    2. User top tracks
    3. User recent tracks
    4. User friends recent tracks

    \f
    :param str username: The user for whom the playlist will be generated
    :param int playlist_type: The playlist type number
    :param int limit: Limit the number of the tracks
    """

    create_or_update_playlist(
        Playlist(
            type=UserPlaylist.from_choice(playlist_type),
            provider=Provider.lastfm,
            arguments=dict(username=username),
            limit=limit,
        )
    )


@add.command("chart")
@click.option(
    "--limit",
    help="The maximum number of tracks",
    type=click.IntRange(50, 1000),
    prompt="Maximum tracks",
    default=50,
)
def add_chart_playlist(limit: int):
    """
    Add a top tracks playlist.

    \f
    :param int limit: Limit the number of the tracks
    """

    create_or_update_playlist(
        Playlist(
            type=ChartPlaylist.CHART, provider=Provider.lastfm, limit=limit
        )
    )


@add.command("country")
@click.option(
    "--country",
    help="An alpha-2 ISO-3166 country code",
    type=CountryParamType(),
    prompt="Country Code",
)
@click.option(
    "--limit",
    help="The maximum number of tracks",
    type=click.IntRange(50, 1000),
    prompt="Maximum tracks",
    default=50,
)
def add_country_playlist(country: str, limit: int):
    """
    Add a top tracks playlist by country.

    \f
    :param str country: An alpha-2 ISO-3166 country code
    :param int limit: Limit the number of the tracks
    """

    create_or_update_playlist(
        Playlist(
            type=ChartPlaylist.COUNTRY,
            provider=Provider.lastfm,
            arguments=dict(country=country),
            limit=limit,
        )
    )


@add.command("tag")
@click.option(
    "--tag",
    help="A last.fm tag, see tags command",
    prompt="Tag",
    type=TagParamType(),
)
@click.option(
    "--limit",
    help="The maximum number of tracks",
    type=click.IntRange(50, 1000),
    prompt="Maximum tracks",
    default=50,
)
def add_tag_playlist(tag: Tag, limit: int):
    """
    Add a top tracks playlist by tag.

    \f
    :param str tag: A tag name eg (rock)
    :param int limit: Limit the number of the tracks
    """

    create_or_update_playlist(
        Playlist(
            type=ChartPlaylist.TAG,
            provider=Provider.lastfm,
            arguments=dict(tag=tag.name),
            limit=limit,
        )
    )


@add.command("artist")
@click.option(
    "--artist", help="An artist name", prompt="Artist", type=ArtistParamType()
)
@click.option(
    "--limit",
    help="The maximum number of tracks",
    type=click.IntRange(50, 1000),
    prompt="Maximum tracks",
    default=50,
)
def add_artist_playlist(artist: Artist, limit: int):
    """
    Add a top tracks playlist by artist.

    \f
    :param str artist: An artist name eg (Queen)
    :param int limit: Limit the number of the tracks
    """

    create_or_update_playlist(
        Playlist(
            type=ChartPlaylist.ARTIST,
            provider=Provider.lastfm,
            arguments=dict(artist=artist.name),
            limit=limit,
        )
    )


@lastfm.command("list")
def list_playlists():
    """List all playlists."""

    values = [
        p.values_list() for p in Playlist.find_by_provider(Provider.lastfm)
    ]
    click.secho(tabulate(values, headers=Playlist.values_header()))


@lastfm.command("remove")
@click.argument("id", required=True)
def remove_playlist(id: str):
    """
    Remove a playlist by id.

    \f
    :param str id: The playlist id
    """

    playlist = Playlist.get(provider=Provider.lastfm, id=id)
    click.confirm("Do you want to continue?", abort=True)
    playlist.remove()
    click.secho("Removed playlist: {}!".format(playlist.id))
