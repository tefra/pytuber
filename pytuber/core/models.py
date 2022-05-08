import base64
import contextlib
import enum
import hashlib
import json
import re
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from dataclasses import replace
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

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
        return asdict(self)


@dataclass
class Config(Document):
    provider: str = field()
    data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.provider = str(self.provider)


@dataclass
class Track(Document):
    artist: str = field()
    name: str = field()
    id: Optional[str] = field(default=None)
    youtube_id: Optional[str] = field(default=None, metadata={"keep": True})

    def __post_init__(self):
        if self.id is None:
            self.id = hashlib.sha1(
                re.sub(
                    r"[\W_]+",
                    "",
                    f"{self.artist}{self.name}".lower(),
                ).encode("utf-8")
            ).hexdigest()[:7]


@dataclass
class Playlist(Document):
    title: str = field()
    type: str = field()
    provider: str = field()
    arguments: dict = field(default_factory=dict)
    id: Optional[str] = field(default=None)
    youtube_id: Optional[str] = field(default=None, metadata={"keep": True})
    tracks: List[str] = field(default_factory=list, metadata={"keep": True})
    synced: Optional[int] = field(default=None, metadata={"keep": True})
    uploaded: Optional[int] = field(default=None, metadata={"keep": True})

    def __post_init__(self):
        self.type = str(self.type)
        self.provider = str(self.provider)

        if self.id is None:
            self.id = hashlib.sha1(
                json.dumps(
                    {
                        key: getattr(self, key)
                        for key in ["arguments", "provider", "type"]
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
        return ", ".join([f"{k}: {v}" for k, v in self.arguments.items()])


@dataclass(order=True)
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

        raise NotFound(f"No {cls.namespace} matched your argument: {key}!")

    @classmethod
    def set(cls, data: Dict):
        obj = cls.model(**data)
        key = getattr(obj, cls.key)

        with contextlib.suppress(KeyError):
            data = Registry.get(cls.namespace, key)
            for f in fields(cls.model):
                if f.metadata.get("keep") and not getattr(obj, f.name):
                    setattr(obj, f.name, data.get(f.name))

        Registry.set(cls.namespace, key, obj.asdict())
        return obj

    @classmethod
    def update(cls, obj, data: Dict):
        new = replace(obj, **data)
        key = getattr(new, cls.key)
        Registry.set(cls.namespace, key, new.asdict())
        return new

    @classmethod
    def remove(cls, key):
        try:
            Registry.remove(cls.namespace, key)
        except KeyError as e:
            raise NotFound(f"No {cls.namespace} matched your argument: {key}!") from e

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
