import datetime
import enum
import hashlib
from typing import Dict

import attr

from pytubefm.data import Registry
from pytubefm.exceptions import NotFound


def timestamp():
    return int(datetime.datetime.utcnow().strftime("%s"))


class Provider(enum.Enum):
    lastfm = "last.fm"
    youtube = "youtube"

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


@attr.s(auto_attribs=True)
class Config(Document):
    provider: str = attr.ib(converter=str)
    data: dict = attr.ib(factory=dict)


class ConfigManager:
    key = "provider_config_%s"

    @classmethod
    def get(cls, provider: Provider):
        try:
            key = cls.key % provider
            data = Registry.get(key)
            return Config(**data)
        except KeyError:
            return None

    @classmethod
    def update(cls, data: Dict):
        key = cls.key % data["provider"]
        config = Config(**data)
        Registry.set(key, config.asdict())


@attr.s
class Playlist(Document):
    type: str = attr.ib(converter=str)
    provider: str = attr.ib(converter=str)
    limit: int = attr.ib(converter=int)
    arguments: dict = attr.ib(factory=dict)
    id: str = attr.ib()
    modified: int = attr.ib(factory=timestamp)
    synced: int = attr.ib(default=None)
    uploaded: int = attr.ib(default=None)

    @id.default
    def generate_id(self):
        def sha1(x):
            return hashlib.sha1(x.encode("utf-8")).hexdigest()[:7]

        parts = [self.arguments[k] for k in sorted(self.arguments.keys())]
        return self.key(self.type, *parts, hash=sha1)

    @property
    def is_new(self):
        return self.synced is None

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


class PlaylistManager:
    key = "provider_playlists_%s"

    @classmethod
    def get(cls, provider: Provider, id: str):
        try:
            key = cls.key % provider
            data = Registry.get(key, id)
            return Playlist(**data)
        except KeyError:
            raise NotFound("No such playlist id: {}!".format(id))

    @classmethod
    def set(cls, data):
        playlist = Playlist(**data)
        try:
            exist = cls.get(playlist.provider, playlist.id)
            playlist.synced = exist.synced
            playlist.uploaded = exist.uploaded
        except NotFound:
            pass
        key = cls.key % playlist.provider
        Registry.set(key, playlist.id, playlist.asdict())
        return playlist

    @classmethod
    def remove(cls, provider: Provider, id: str):
        try:
            key = cls.key % provider
            Registry.remove(key, id)
            # Track.remove_by_playlist_id(self.id)
        except KeyError:
            raise NotFound("No such playlist id: {}!".format(id))

    @classmethod
    def find(cls, provider: Provider):
        key = cls.key % provider
        entries = Registry.get(key, default={})
        return [Playlist(**entry) for entry in entries.values()]
