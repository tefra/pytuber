import os
from enum import Enum

import appdirs
import attr
from tinydb import Query, TinyDB
from tinydb.database import Table


class Provider(Enum):
    lastfm = "last.fm"
    youtube = "youtube"


@attr.s()
class Document:
    db: TinyDB

    def asdict(self):
        return attr.asdict(self)

    @classmethod
    def get_db(cls) -> TinyDB:
        if Document.db is None:
            config_dir = appdirs.user_config_dir("pytubefm", False)
            Document.db = TinyDB(
                os.path.join(config_dir, "data"), create_dirs=True
            )
        return Document.db

    @classmethod
    def table(cls) -> Table:
        return cls.get_db().table(cls.__name__)

    @classmethod
    def from_doc(cls, doc):
        return cls(**doc)


@attr.s(auto_attribs=True)
class Config(Document):
    provider: str
    data: dict

    @classmethod
    def find_by_provider(cls, provider: Provider):
        document = cls.table().get(Query().provider == provider.value)
        if document:
            return cls.from_doc(document)

    def save(self):
        return self.table().upsert(
            self.asdict(), Query().provider == self.provider
        )
