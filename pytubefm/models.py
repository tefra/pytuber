import enum
import hashlib
import json
import re
from contextlib import suppress
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


@attr.s
class Track(Document):
    artist: str = attr.ib()
    name: str = attr.ib()
    duration: int = attr.ib()
    id: str = attr.ib()
    url: str = attr.ib()

    @id.default
    def generate_id(self):
        return hashlib.sha1(
            re.sub(
                r"[\W_]+", "", "{}{}".format(self.artist, self.name).lower()
            ).encode("utf-8")
        ).hexdigest()[:7]

    @url.default
    def generate_url(self):
        with suppress(NotFound):
            self.url = TrackManager.get(self.id).url


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
    tracks: List[str] = attr.ib(factory=list)

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
        except KeyError:
            raise NotFound("No such playlist id: {}!".format(id))

    @classmethod
    def update(cls, playlist: Playlist, data: Dict):

        if len(data.get("tracks", [])) > 0:
            data["synced"] = timestamp()

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
    key = "tracks"

    @classmethod
    def get(cls, id: str):
        try:
            data = Registry.get(cls.key, id)
            return Track(**data)
        except KeyError:
            raise NotFound("No such track id: {}!".format(id))

    @classmethod
    def add(cls, tracks: List[pydrag.Track]):
        track_ids = []
        for entry in tracks:
            track = Track(
                artist=entry.artist.name,
                name=entry.name,
                duration=entry.duration,
            )
            track_ids.append(track.id)
            Registry.set(cls.key, track.id, track.asdict())
        return track_ids

    @classmethod
    def find(cls, ids):
        return [cls.get(id) for id in ids]

    @classmethod
    def remove(cls, id: str):
        try:
            Registry.remove(cls.key, id)
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
