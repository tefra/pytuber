import json
from functools import reduce


class Singleton(type):
    _obj: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._obj:
            cls._obj[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._obj[cls]


class Registry(dict, metaclass=Singleton):
    @classmethod
    def get(cls, *keys, default=None):
        return reduce(dict.__getitem__, keys, cls())

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
        with open(path, "w") as fp:
            json.dump(cls(), fp)

    @classmethod
    def from_file(cls, path: str):
        try:
            with open(path, "r") as cfg:
                data = json.load(cfg)
        except FileNotFoundError:
            data = dict()
        return cls(data)
