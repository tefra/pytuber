import base64
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
    youtube_id: str = attr.ib()

    @id.default
    def generate_id(self):
        return hashlib.sha1(
            re.sub(
                r"[\W_]+", "", "{}{}".format(self.artist, self.name).lower()
            ).encode("utf-8")
        ).hexdigest()[:7]

    @youtube_id.default
    def generate_youtube_id(self):
        with suppress(NotFound):
            self.youtube_id = TrackManager.get(self.id).video_id


@attr.s
class Playlist(Document):
    type: str = attr.ib(converter=str)
    provider: str = attr.ib(converter=str)
    limit: int = attr.ib(converter=int, cmp=False)
    arguments: dict = attr.ib(factory=dict)
    id: str = attr.ib()
    title: str = attr.ib(default=None)
    youtube_id: str = attr.ib(default=None)
    tracks: List[str] = attr.ib(factory=list)
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

    @property
    def mime(self):
        return base64.b64encode(
            json.dumps(
                {
                    field: getattr(self, field)
                    for field in ["arguments", "provider", "type"]
                }
            ).encode()
        ).decode("utf-8")

    @property
    def display_type(self):
        return (
            self.title if self.title else self.type.replace("_", " ").title()
        )

    @property
    def display_arguments(self):
        return ", ".join(
            ["{}: {}".format(k, v) for k, v in self.arguments.items()]
        )


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
    def find(cls, ids=None):
        if ids is None:
            return [
                Track(**data)
                for data in Registry.get(cls.key, default={}).values()
            ]
        return [cls.get(id) for id in ids]

    @classmethod
    def update(cls, track: Track, data: Dict):
        track = attr.evolve(track, **data)
        Registry.set(cls.key, track.id, track.asdict())
        return track


class History:
    namespace = "history"

    @classmethod
    def set(cls, *args, **kwargs):
        for key, value in kwargs.items():
            Registry.set(cls.namespace, key, value)

    @classmethod
    def get(cls, key, default=None):
        return Registry.get(cls.namespace, key, default=default)
