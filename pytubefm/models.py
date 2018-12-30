import datetime
import enum
import functools
import hashlib
import os

import attr
import click
import pickledb

from pytubefm.exceptions import NotFound, RecordExists


def cached_property(fun):
    """
    A memoize decorator for class properties.

    http://code.activestate.com/recipes/576563-cached-property/#c3
    """

    @functools.wraps(fun)
    def get(self):
        try:
            return self._cache[fun]
        except AttributeError:
            self._cache = {}
        except KeyError:
            pass
        ret = self._cache[fun] = fun(self)
        return ret

    return property(get)


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


class Storage:
    def asdict(self):
        return attr.asdict(self)

    @classmethod
    def storage(cls) -> pickledb.pickledb:
        """
        :return: A pickedb instance.
        :rtype: :class:`pickledb.pickledb`
        """
        if not getattr(Storage, "db", None):
            db = pickledb.load(
                os.path.join(
                    click.get_app_dir("pytubefm", False), "storage.db"
                ),
                True,
            )
            setattr(Storage, "db", db)

        return getattr(Storage, "db")

    @classmethod
    def key(cls, *args, hash=str):
        prefix = cls.__name__.lower()
        key = [str(x) for x in args]
        key.insert(0, prefix)
        return hash("_".join(key))

    @classmethod
    def date(cls, timestamp: int):
        return (
            datetime.datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M"
            )
            if timestamp
            else "-"
        )

    @staticmethod
    def now():
        return datetime.datetime.now()


@attr.s(auto_attribs=True)
class Config(Storage):
    provider: str
    data: dict

    @classmethod
    def find_by_provider(cls, provider: Provider):
        data = cls.storage().get(cls.key(provider))
        if data:
            return cls(**data)
        return None

    def save(self) -> bool:
        return self.storage().set(self.key(self.provider), self.asdict())


@attr.s
class Playlist(Storage):
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

    @cached_property
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

        if not self.storage().exists(self.group):
            self.storage().dcreate(self.group)

        return self.storage().dadd(self.group, (self.id, self.asdict()))

    def remove(self):
        try:
            self.storage().dpop(self.group, self.id)
            return True
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
            return Playlist(**cls.storage().dget(cls.key(provider), id))
        except KeyError:
            raise NotFound("No such playlist id: {}!".format(id))

    @classmethod
    def find_by_provider(cls, provider: Provider):
        group = cls.key(provider)
        if not cls.storage().exists(group):
            return []
        return [cls(**data) for data in cls.storage().dgetall(group).values()]
