import os
from enum import Enum

import appdirs
import attr
import pickledb


class Provider(Enum):
    lastfm = "last.fm"
    youtube = "youtube"

    def __str__(self):
        return self.value


@attr.s()
class Document:
    db: pickledb

    def asdict(self):
        return attr.asdict(self)

    @classmethod
    def storage(cls) -> pickledb:
        if Document.db is None:
            config_dir = appdirs.user_config_dir("pytubefm", False)
            Document.db = pickledb.load(
                os.path.join(config_dir, "storage.db"), True
            )
        return Document.db

    @classmethod
    def key(cls, *args):
        prefix = cls.__class__.__name__.lower()
        key = [str(x) for x in args]
        key.insert(0, prefix)
        return "_".join(key)


@attr.s(auto_attribs=True)
class Config(Document):
    provider: str
    data: dict

    @classmethod
    def find_by_provider(cls, provider: Provider):
        data = cls.storage().get(cls.key(provider))
        if data:
            return cls(**data)
        return None

    def save(self):
        return self.storage().set(self.key(self.provider), self.asdict())
