from functools import partial

import click

from pytuber.lastfm.models import PlaylistType, UserPlaylistType
from pytuber.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
    UserParamType,
)
from pytuber.models import History, PlaylistManager, Provider


@click.group("lastfm")
def lastfm_playlist():
    """Last.fm is a music service that learns what you love."""


option_limit = partial(
    click.option,
    "--limit",
    help="The maximum number of tracks",
    type=click.IntRange(50, 1000),
    prompt="Maximum tracks",
    default=lambda: History.get("limit", 50),
)
option_title = partial(click.option, "--title", help="title", prompt="Title")


@lastfm_playlist.command()
@click.option(
    "--user",
    help="The user for whom the playlist will be generated",
    prompt="Last.fm username",
    type=UserParamType(),
    default=lambda: History.get("user", default=None),
)
@click.option(
    "--playlist-type",
    help="The playlist type number",
    type=UserPlaylistType.range(),
    prompt=UserPlaylistType.choices(),
)
@option_limit()
@option_title()
def user_playlist(user: str, playlist_type: int, limit: int, title: str):
    """
    Add a user type playlist. This type of playlists are based on a user's
    music preference and history.

    \b
    Playlist types:
    1. User loved tracks
    2. User top tracks
    3. User recent tracks
    4. User friends recent tracks
    """
    History.set(user=user, limit=limit)
    playlist = PlaylistManager.set(
        dict(
            type=UserPlaylistType.from_choice(playlist_type),
            provider=Provider.lastfm,
            arguments=dict(username=user, limit=limit),
            title=title.strip(),
        )
    )
    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
        )
    )


@lastfm_playlist.command()
@option_limit()
@option_title()
def chart_playlist(limit: int, title: str):
    """Add a top tracks playlist."""

    History.set(limit=limit)
    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.CHART,
            provider=Provider.lastfm,
            arguments=dict(limit=limit),
            title=title.strip(),
        )
    )
    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
        )
    )


@lastfm_playlist.command()
@click.option(
    "--country",
    help="An alpha-2 ISO-3166 country code",
    type=CountryParamType(),
    prompt="Country Code",
)
@option_limit()
@option_title()
def country_playlist(country: str, limit: int, title: str):
    """Add a top tracks playlist by country."""

    History.set(limit=limit)
    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.COUNTRY,
            provider=Provider.lastfm,
            arguments=dict(country=country, limit=limit),
            title=title.strip(),
        )
    )
    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
        )
    )


@lastfm_playlist.command()
@click.option(
    "--tag",
    help="A last.fm tag, see tags command",
    prompt="Tag",
    type=TagParamType(),
)
@option_limit()
@option_title()
def tag_playlist(tag: str, limit: int, title: str):
    """Add a top tracks playlist by tag."""

    History.set(limit=limit)
    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.TAG,
            provider=Provider.lastfm,
            arguments=dict(tag=tag, limit=limit),
            title=title.strip(),
        )
    )

    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
        )
    )


@lastfm_playlist.command()
@click.option(
    "--artist", help="An artist name", prompt="Artist", type=ArtistParamType()
)
@option_limit()
@option_title()
def artist_playlist(artist: str, limit: int, title: str):
    """Add a top tracks playlist by artist."""

    History.set(limit=limit)
    playlist = PlaylistManager.set(
        dict(
            type=PlaylistType.ARTIST,
            provider=Provider.lastfm,
            arguments=dict(artist=artist, limit=limit),
            title=title.strip(),
        )
    )

    click.secho(
        "{} playlist: {}!".format(
            "Updated" if playlist.synced else "Added", playlist.id
        )
    )
