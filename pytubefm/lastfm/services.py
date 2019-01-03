from typing import List

import click
from pydrag import Tag, configure

from pytubefm.data import Registry
from pytubefm.exceptions import ConfigMissing
from pytubefm.iso3166 import countries
from pytubefm.models import Config, Document, Provider


class LastService(Document):
    def __init__(self):
        try:
            config = Config.find_by_provider(Provider.lastfm)
            configure(api_key=config.data["api_key"])
        except (KeyError, AttributeError):
            raise ConfigMissing(
                "Please run setup before calling any last.fm api webservices"
            )

    def get_tags(self, refresh=False) -> List[Tag]:
        """
        Return a list of the most popular last.fm tags.

        :rtype: :class:`pydrag.Tag`
        """
        key = self.key(Provider.lastfm)
        if refresh or key not in Registry():

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

            Registry.set(key, tags)

        return [Tag(**data) for data in Registry.get(key)]

    @classmethod
    def get_country_by_code(cls, _, __, value):
        """
        Get the country name in english by iso-3166 alpha2 code
        Source: `iso.org <https://www.iso.org/obp/ui/#search./>`_
        :param  str code:
        :rtype: str
        """
        try:
            return countries[value.upper()].lower()
        except KeyError:
            raise click.BadParameter(
                "Unkown iso-3166 country code: {}".format(value.upper)
            )
