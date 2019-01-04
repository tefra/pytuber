from datetime import timedelta
from typing import List

import click
from pydrag import Artist, Tag, configure

from pytubefm.data import Registry
from pytubefm.models import Config, Provider


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
    def assert_config(cls):
        """
        Assert last.fm configuration exists.

        :raise :class:`click.Abort`
        """
        try:
            config = Config.find_by_provider(Provider.lastfm)
            configure(api_key=config.data["api_key"])
        except (KeyError, AttributeError):
            click.secho("Run setup to configure last.fm services")
            raise click.Abort()
