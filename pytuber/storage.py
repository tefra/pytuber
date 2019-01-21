import json
import time
from contextlib import suppress
from datetime import timedelta
from functools import reduce
from json import JSONDecodeError
from typing import Callable, Dict


class Singleton(type):
    _obj: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._obj:
            cls._obj[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._obj[cls]


NOTHING = object()


class Registry(dict, metaclass=Singleton):
    @classmethod
    def exists(cls, *keys):
        try:
            reduce(dict.__getitem__, keys, cls())
            return True
        except KeyError:
            return False

    @classmethod
    def get(cls, *keys, default=NOTHING):
        try:
            return reduce(dict.__getitem__, keys, cls())
        except KeyError:
            if default == NOTHING:
                raise
            return default

    @classmethod
    def set(cls, *args):
        data = cls()
        *keys, value = args

        for key in keys[:-1]:
            data = data.setdefault(key, {})
        data[keys[-1]] = value

    @classmethod
    def remove(cls, *args):
        data = cls()

        for key in args[:-1]:
            data = data[key]
        del data[args[-1]]

    @classmethod
    def clear(cls):
        dict.clear(cls())

    @classmethod
    def persist(cls, path):
        with suppress(FileNotFoundError):
            with open(path, "w") as fp:
                json.dump(cls(), fp)

    @classmethod
    def from_file(cls, path: str):
        data: Dict = dict()
        with suppress(FileNotFoundError, JSONDecodeError):
            with open(path, "r") as cfg:
                data = json.load(cfg)
        return cls(data)

    @classmethod
    def cache(
        cls, key: str, func: Callable, ttl: timedelta, refresh: bool = False
    ):
        registry = cls()
        if refresh or key not in registry or registry[key][1] < time.time():
            registry[key] = (func(), time.time() + ttl.total_seconds())
        return registry[key][0]
