from datetime import timedelta
from typing import List

import click
from pydrag import Artist, Tag, Track, User, configure
from pydrag.constants import Period

from pytubefm.data import Registry
from pytubefm.lastfm.models import PlaylistType
from pytubefm.models import ConfigManager, Provider


class LastService:
    @classmethod
    def get_tracks(cls, type, limit, **kwargs):
        cls.assert_config()
        ptype = PlaylistType(type)
        if ptype == PlaylistType.USER_LOVED_TRACKS:
            user = cls.get_user(kwargs["username"])
            return user.get_loved_tracks(limit=limit)
        elif ptype == PlaylistType.USER_RECENT_TRACKS:
            user = cls.get_user(kwargs["username"])
            return user.get_recent_tracks(limit=limit)
        elif ptype == PlaylistType.USER_TOP_TRACKS:
            user = cls.get_user(kwargs["username"])
            return user.get_top_tracks(period=Period.overall, limit=limit)
        elif ptype == PlaylistType.USER_FRIENDS_RECENT_TRACKS:
            user = cls.get_user(kwargs["username"])
            friends = user.get_friends(limit=limit, recent_tracks=True)
            return [f.recent_track for f in friends if f.recent_track]
        elif ptype == PlaylistType.CHART:
            return Track.get_top_tracks_chart(limit=limit)
        elif ptype == PlaylistType.COUNTRY:
            return Track.get_top_tracks_by_country(
                country=kwargs["country"], limit=limit
            )
        elif ptype == PlaylistType.TAG:
            tag = cls.get_tag(kwargs["tag"])
            return tag.get_top_tracks(limit=limit)
        elif ptype == PlaylistType.ARTIST:
            artist = cls.get_artist(kwargs["artist"])
            return artist.get_top_tracks(limit=limit)

    @classmethod
    def get_tags(cls, refresh=False) -> List[Tag]:
        """
        Return a list of the most popular last.fm tags. The result will be
        cached for 30 days.

        \f
        :rtype: :class:`list` of :class:`pydrag.Tag`
        """

        cls.assert_config()

        def retrieve_tags():
            page = 1
            tags = []  # type: List[dict]
            with click.progressbar(length=4, label="Fetching tags") as bar:
                while len(tags) < 1000:
                    tags.extend(
                        [
                            t.to_dict()
                            for t in Tag.get_top_tags(limit=250, page=page)
                        ]
                    )
                    bar.update(page)
                    page += 1
            return tags

        return [
            Tag(**data)
            for data in Registry.cache(
                key="last.fm_tag_list",
                ttl=timedelta(days=30),
                func=retrieve_tags,
                refresh=refresh,
            )
        ]

    @classmethod
    def get_tag(cls, name) -> Tag:
        tags = cls.get_tags()
        return [tag for tag in tags if tag.name.lower() == name.lower()][0]

    @classmethod
    def get_artist(cls, artist: str) -> Artist:
        """
        Use last.fm api to find an artist by name. The result will be cached
        for 30 days.

        :param str artist: The artist's name
        :rtype: :class:`pydrag.Artist`
        """
        cls.assert_config()

        cache = Registry.cache(
            key="last.fm_artist_{}".format(artist),
            ttl=timedelta(days=30),
            func=lambda: Artist.find(artist).to_dict(),
        )
        return Artist(**cache)

    @classmethod
    def get_user(cls, username) -> User:
        """
        Use last.fm api to fetch a user by name. The result will be cached for
        24 hours.

        :param str username: The user's name
        :rtype: :class:`pydrag.User`
        """
        cls.assert_config()

        cache = Registry.cache(
            key="last.fm_user_{}".format(username.lower()),
            ttl=timedelta(hours=24),
            func=lambda: User.find(username).to_dict(),
        )
        return User(**cache)

    @classmethod
    def assert_config(cls):
        """
        Assert last.fm configuration exists.

        :raise :class:`click.Abort`
        """
        try:
            config = ConfigManager.get(Provider.lastfm)
            configure(api_key=config.data["api_key"])
        except (KeyError, AttributeError):
            click.secho("Run setup to configure last.fm services")
            raise click.Abort()
