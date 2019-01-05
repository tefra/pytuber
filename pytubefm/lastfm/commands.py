from datetime import timedelta
from typing import Optional, Tuple

import click
from pydrag import Artist, Tag, User
from tabulate import tabulate

from pytubefm.lastfm.models import PlaylistType, UserPlaylistType
from pytubefm.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
    UserParamType,
)
from pytubefm.lastfm.services import LastService
from pytubefm.models import (
    ConfigManager,
    PlaylistManager,
    Provider,
    TrackManager,
    date,
)


@click.group()
def lastfm():
    pass


@lastfm.group()
def add():
    """Created or update a playlist."""


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

    if ConfigManager.get(Provider.lastfm):
        click.confirm("Overwrite existing configuration?", abort=True)

    ConfigManager.update(
        dict(provider=Provider.lastfm.value, data=dict(api_key=api_key))
    )
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
    "--user",
    help="The user for whom the playlist will be generated",
    prompt="Last.fm username",
    type=UserParamType(),
)
@click.option(
    "--playlist-type",
    help="The playlist type number",
    type=UserPlaylistType.range(),
    prompt=UserPlaylistType.choices(),
)
@click.option(
    "--limit",
    help="The maximum number of tracks",
    type=click.IntRange(50, 1000),
    prompt="Maximum tracks",
    default=50,
)
def add_user_playlist(user: User, playlist_type: int, limit: int):
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
    :param User user: The user for whom the playlist will be generated
    :param int playlist_type: The playlist type number
    :param int limit: Limit the number of the tracks
    """

    playlist = PlaylistManager.set(
        dict(
            type=UserPlaylistType.from_choice(playlist_type),
            provider=Provider.lastfm,
            arguments=dict(username=user.name),
            limit=limit,
        )
    )
    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
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

    playlist = PlaylistManager.set(
        dict(type=PlaylistType.CHART, provider=Provider.lastfm, limit=limit)
    )
    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
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

    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.COUNTRY,
            provider=Provider.lastfm,
            arguments=dict(country=country),
            limit=limit,
        )
    )
    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
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

    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.TAG,
            provider=Provider.lastfm,
            arguments=dict(tag=tag.name),
            limit=limit,
        )
    )

    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
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

    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.ARTIST,
            provider=Provider.lastfm,
            arguments=dict(artist=artist.name),
            limit=limit,
        )
    )

    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
        )
    )


@lastfm.command("list")
@click.argument("id", required=False)
def list_playlists(id: Optional[str]):
    """List all playlists or the tracks of a playlist if you provider an id."""

    if id:
        playlist = PlaylistManager.get(Provider.lastfm, id)
        click.echo_via_pager(
            tabulate(
                [
                    (
                        t.artist,
                        t.name,
                        str(timedelta(seconds=t.duration))
                        if t.duration
                        else "-",
                    )
                    for t in TrackManager.find(playlist.id)
                ],
                showindex=True,
                headers=("No", "Artist", "Track Name", "Duration"),
            )
        )
    else:
        click.secho(
            tabulate(
                [
                    (
                        p.id,
                        p.type.replace("_", " ").title(),
                        ", ".join(
                            [
                                "{}: {}".format(k, v)
                                for k, v in p.arguments.items()
                            ]
                        ),
                        p.limit,
                        date(p.modified),
                        date(p.synced),
                        date(p.uploaded),
                    )
                    for p in PlaylistManager.find(Provider.lastfm)
                ],
                headers=(
                    "ID",
                    "Type",
                    "Arguments",
                    "Limit",
                    "Modified",
                    "Synced",
                    "Uploaded",
                ),
            )
        )


@lastfm.command("remove")
@click.argument("ids", required=True, nargs=-1)
def remove_playlists(ids: Tuple[str]):
    """
    Remove one or more playlists by id.

    \f
    :param tuple id: A list of playlist ids to remove
    """

    click.confirm("Do you want to continue?", abort=True)
    for id in ids:
        PlaylistManager.remove(Provider.lastfm, id)
        click.secho("Removed playlist: {}!".format(id))


@lastfm.command("sync")
@click.argument("ids", required=False, nargs=-1)
def sync_playlists(ids: Tuple[str]):
    """
    Sync all or one or more playlists by id.

    \f
    :param tuple id: A list of playlist ids to remove
    """

    playlists = PlaylistManager.find(Provider.lastfm)
    if ids:
        playlists = list(filter(lambda x: x.id in ids, playlists))

    with click.progressbar(playlists, label="Syncing playlists") as bar:
        for playlist in bar:
            tracklist = LastService.get_tracks(
                type=playlist.type, limit=playlist.limit, **playlist.arguments
            )
            TrackManager.set(playlist, tracklist)
