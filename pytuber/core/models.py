import base64
import contextlib
import enum
import hashlib
import json
import re
from typing import Dict, List, Type

import attr

from pytuber.exceptions import NotFound
from pytuber.storage import Registry
from pytuber.utils import timestamp


class StrEnum(enum.Enum):
    def __str__(self):
        return self.value


class Provider(StrEnum):
    lastfm = "last.fm"
    youtube = "youtube"
    user = "user"


class PlaylistType(StrEnum):
    EDITOR = "editor"
    FILE = "file"


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
    id: str = attr.ib(default=None)
    youtube_id: str = attr.ib(default=None, metadata=dict(keep=True))

    def __attrs_post_init__(self):
        if self.id is None:
            self.id = hashlib.sha1(
                re.sub(
                    r"[\W_]+",
                    "",
                    "{}{}".format(self.artist, self.name).lower(),
                ).encode("utf-8")
            ).hexdigest()[:7]


@attr.s
class Playlist(Document):
    title: str = attr.ib(converter=str)
    type: str = attr.ib(converter=str)
    provider: str = attr.ib(converter=str)
    arguments: dict = attr.ib(factory=dict)
    id: str = attr.ib(default=None)
    youtube_id: str = attr.ib(default=None, metadata=dict(keep=True))
    tracks: List[str] = attr.ib(factory=list, metadata=dict(keep=True))
    synced: int = attr.ib(default=None, metadata=dict(keep=True))
    uploaded: int = attr.ib(default=None, metadata=dict(keep=True))

    def __attrs_post_init__(self):
        if self.id is None:
            self.id = hashlib.sha1(
                json.dumps(
                    {
                        field: getattr(self, field)
                        for field in ["arguments", "provider", "type"]
                    }
                ).encode("utf-8")
            ).hexdigest()[:7]

    @property
    def youtube_url(self):
        link = "https://www.youtube.com/playlist?list={}"
        return link.format(self.youtube_id) if self.youtube_id else "-"

    @property
    def mime(self):
        return base64.b64encode(
            json.dumps(
                {
                    field: getattr(self, field)
                    for field in ["arguments", "provider", "type", "title"]
                }
            ).encode()
        ).decode("utf-8")

    @classmethod
    def from_mime(cls, mime):
        with contextlib.suppress(Exception):
            return cls(**json.loads(base64.b64decode(mime)))
        return None

    @property
    def display_arguments(self):
        return ", ".join(
            ["{}: {}".format(k, v) for k, v in self.arguments.items()]
        )


@attr.s(auto_attribs=True)
class PlaylistItem(Document):
    id: str
    name: str
    artist: str
    video_id: str


class Manager:
    namespace: str
    model: Type
    key: str

    @classmethod
    def keys(cls):
        return list(Registry.get(cls.namespace, default={}).keys())

    @classmethod
    def exists(cls, obj):
        key = getattr(obj, cls.key)
        return Registry.exists(cls.namespace, key)

    @classmethod
    def get(cls, key, **kwargs):
        with contextlib.suppress(KeyError):
            data = Registry.get(cls.namespace, str(key), **kwargs)
            with contextlib.suppress(TypeError):
                return cls.model(**data)
            return data

        raise NotFound(
            "No {} matched your argument: {}!".format(cls.namespace, key)
        )

    @classmethod
    def set(cls, data: Dict):
        obj = cls.model(**data)
        key = getattr(obj, cls.key)

        with contextlib.suppress(KeyError):
            data = Registry.get(cls.namespace, key)
            for field in attr.fields(cls.model):
                if field.metadata.get("keep") and not getattr(obj, field.name):
                    setattr(obj, field.name, data.get(field.name))

        Registry.set(cls.namespace, key, obj.asdict())
        return obj

    @classmethod
    def update(cls, obj, data: Dict):
        new = attr.evolve(obj, **data)
        key = getattr(new, cls.key)
        Registry.set(cls.namespace, key, new.asdict())
        return new

    @classmethod
    def remove(cls, key):
        try:
            Registry.remove(cls.namespace, key)
        except KeyError:
            raise NotFound(
                "No {} matched your argument: {}!".format(cls.namespace, key)
            )

    @classmethod
    def find(cls, **kwargs):
        def match(data, conditions):
            with contextlib.suppress(Exception):
                for k, v in conditions.items():
                    value = data.get(k)
                    if callable(v):
                        assert v(value)
                    elif v is None:
                        assert value is None
                    else:
                        assert type(value)(v) == value
                return True
            return False

        return [
            cls.model(**raw)
            for raw in Registry.get(cls.namespace, default={}).values()
            if match(raw, kwargs)
        ]


class ConfigManager(Manager):
    namespace = "configuration"
    key = "provider"
    model = Config


class PlaylistManager(Manager):
    namespace = "playlist"
    key = "id"
    model = Playlist

    @classmethod
    def update(cls, obj, data: Dict):
        if len(data.get("tracks", [])) > 0:
            data["synced"] = timestamp()

        return super().update(obj, data)


class TrackManager(Manager):
    namespace = "track"
    key = "id"
    model = Track

    @classmethod
    def find_youtube_id(cls, id: str):
        return Registry.get(cls.namespace, id, "youtube_id", default=None)


class History:
    namespace = "history"

    @classmethod
    def set(cls, *args, **kwargs):
        for key, value in kwargs.items():
            Registry.set(cls.namespace, key, value)

    @classmethod
    def get(cls, key, default=None):
        return Registry.get(cls.namespace, key, default=default)
