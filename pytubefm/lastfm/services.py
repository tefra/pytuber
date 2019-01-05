from datetime import timedelta
from typing import List

import click
from pydrag import Artist, Tag, User, configure

from pytubefm.data import Registry
from pytubefm.models import ConfigManager, Provider


class LastService:
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
            key="last.fm_user_{}".format(username),
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
