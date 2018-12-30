from typing import List

import click
from pydrag import Tag, configure

from pytubefm.exceptions import ConfigMissing
from pytubefm.iso3166 import countries
from pytubefm.models import Config, Provider, Storage


class LastService(Storage):
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
        if refresh or not self.storage().exists(key):
            self.storage().auto_dump = False
            self.storage().set(key, [])
            page = 1

            with click.progressbar(length=4, label="Fetching tags") as bar:
                while self.storage().llen(key) < 1000:
                    tags = Tag.get_top_tags(limit=250, page=page)
                    self.storage().lextend(key, [t.to_dict() for t in tags])
                    bar.update(page)
                    page += 1
                self.storage().auto_dump = True
                self.storage().dump()

        return [Tag(**data) for data in self.storage().lgetall(key)]

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
