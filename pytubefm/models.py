import datetime
import enum
import hashlib
import os

import attr
import click

from pytubefm.data import Registry
from pytubefm.exceptions import NotFound, RecordExists


class Provider(enum.Enum):
    lastfm = "last.fm"
    youtube = "youtube"

    def __str__(self):
        return self.value


class PlaylistType(enum.Enum):
    @classmethod
    def choices(cls):
        prompts = ["Playlist Types"]
        prompts.extend(
            ["[{}] {}".format(i + 1, str(x)) for i, x in enumerate(cls)]
        )
        prompts.extend(["Select a playlist type 1-{}".format(len(cls))])
        return os.linesep.join(prompts)

    @classmethod
    def range(cls):
        return click.IntRange(1, len(cls))

    @classmethod
    def from_choice(cls, choice: int) -> "PlaylistType":
        return list(cls)[choice - 1]

    def __str__(self):
        return self.value


class Document:
    def asdict(self):
        return attr.asdict(self)

    @classmethod
    def key(cls, *args, hash=str):
        prefix = cls.__name__.lower()
        key = [str(x) for x in args]
        key.insert(0, prefix)
        return hash("_".join(key))

    @classmethod
    def date(cls, timestamp: int):
        return (
            datetime.datetime.utcfromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M"
            )
            if timestamp
            else "-"
        )

    @staticmethod
    def now():
        return datetime.datetime.utcnow()


@attr.s(auto_attribs=True)
class Config(Document):
    provider: str
    data: dict

    @classmethod
    def find_by_provider(cls, provider: Provider):
        try:
            return cls(**Registry.get(cls.key(provider)))
        except KeyError:
            return None

    def save(self):
        Registry.set(self.key(self.provider), self.asdict())


@attr.s
class Playlist(Document):
    type: str = attr.ib(converter=str)
    provider: str = attr.ib(converter=str)
    limit: int = attr.ib(converter=int)
    arguments: dict = attr.ib(factory=dict)
    id: str = attr.ib()
    modified: int = attr.ib()
    synced: int = attr.ib(default=None)
    uploaded: int = attr.ib(default=None)

    @modified.default
    def generate_now(self):
        return int(self.now().strftime("%s"))

    @id.default
    def generate_id(self):
        def sha1(x):
            return hashlib.sha1(x.encode("utf-8")).hexdigest()[:7]

        parts = [self.arguments[k] for k in sorted(self.arguments.keys())]
        return self.key(self.type, *parts, hash=sha1)

    @property
    def group(self):
        return self.key(self.provider)

    def save(self, overwrite=False):
        try:
            old = self.get(provider=self.provider, id=self.id)
            if not overwrite:
                raise RecordExists("Playlist already exists!")

            self.synced = old.synced
            self.uploaded = old.uploaded
        except NotFound:
            pass

        Registry.set(self.group, self.id, self.asdict())

    def remove(self):
        try:
            Registry.remove(self.group, self.id)
        except KeyError:
            raise NotFound("No such playlist id: {}!".format(self.id))

    def values_list(self):
        return (
            self.id,
            self.type.replace("_", " ").title(),
            ", ".join(
                ["{}: {}".format(k, v) for k, v in self.arguments.items()]
            ),
            self.limit,
            self.date(self.modified),
            self.date(self.synced),
            self.date(self.uploaded),
        )

    @classmethod
    def values_header(cls):
        return (
            "ID",
            "Type",
            "Arguments",
            "Limit",
            "Modified",
            "Synced",
            "Uploaded",
        )

    @classmethod
    def get(cls, provider, id):
        try:
            group = cls.key(provider)
            return cls(**Registry.get(group, id))
        except KeyError:
            raise NotFound("No such playlist id: {}!".format(id))

    @classmethod
    def find_by_provider(cls, provider: Provider):
        try:
            group = cls.key(provider)
            return [cls(**data) for data in Registry.get(group).values()]
        except KeyError:
            return []
