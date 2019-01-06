import enum
import hashlib
import json
from datetime import datetime
from typing import Dict, List

import attr
import pydrag

from pytubefm.exceptions import NotFound
from pytubefm.storage import Registry


def timestamp():
    return int(datetime.utcnow().strftime("%s"))


def date(timestamp: int):
    if not timestamp:
        return "-"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


class Provider(enum.Enum):
    lastfm = "last.fm"
    youtube = "youtube"

    def __str__(self):
        return self.value


class Document:
    def asdict(self):
        return attr.asdict(self)


@attr.s(auto_attribs=True)
class Config(Document):
    provider: str = attr.ib(converter=str)
    data: dict = attr.ib(factory=dict)


@attr.s(auto_attribs=True)
class Track(Document):
    artist: str
    name: str
    duration: int


@attr.s
class Playlist(Document):
    type: str = attr.ib(converter=str)
    provider: str = attr.ib(converter=str)
    limit: int = attr.ib(converter=int, cmp=False)
    arguments: dict = attr.ib(factory=dict)
    id: str = attr.ib()
    modified: int = attr.ib(factory=timestamp, cmp=False)
    synced: int = attr.ib(default=None, cmp=False)
    uploaded: int = attr.ib(default=None, cmp=False)

    @id.default
    def generate_id(self):
        return hashlib.sha1(
            json.dumps(
                {
                    field: getattr(self, field)
                    for field in ["arguments", "provider", "type"]
                }
            ).encode("utf-8")
        ).hexdigest()[:7]


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
        History.set(data)
        return playlist

    @classmethod
    def remove(cls, provider: Provider, id: str):
        try:
            key = cls.key % provider
            Registry.remove(key, id)
            TrackManager.remove(id)
        except KeyError:
            raise NotFound("No such playlist id: {}!".format(id))

    @classmethod
    def update(cls, playlist: Playlist, data: Dict):
        playlist = attr.evolve(playlist, **data)
        key = cls.key % playlist.provider
        Registry.set(key, playlist.id, playlist.asdict())
        return playlist

    @classmethod
    def find(cls, provider: Provider):
        key = cls.key % provider
        entries = Registry.get(key, default={})
        return [Playlist(**entry) for entry in entries.values()]


class TrackManager:
    key = "playlist_tracks_%s"

    @classmethod
    def set(cls, playlist: Playlist, tracks: List[pydrag.Track]):
        def prepare(entry: pydrag.Track):
            return Track(
                artist=entry.artist.name,
                name=entry.name,
                duration=entry.duration,
            ).asdict()

        data = [prepare(track) for track in tracks]
        key = cls.key % playlist.id
        Registry.set(key, data)
        return PlaylistManager.update(playlist, dict(synced=timestamp()))

    @classmethod
    def find(cls, id):
        key = cls.key % id
        entries = Registry.get(key, default=[])
        return [Track(**entry) for entry in entries]

    @classmethod
    def remove(cls, id: str):
        try:
            key = cls.key % id
            Registry.remove(key)
        except KeyError:
            pass


class History:
    namespace = "history"

    @classmethod
    def set(cls, *args, **kwargs):
        for key, value in kwargs.items():
            Registry.set(cls.namespace, key, value)

    @classmethod
    def get(cls, key, default=None):
        return Registry.get(cls.namespace, key, default=default)
