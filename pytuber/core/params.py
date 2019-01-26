import os

import click
from click_completion import completion_configuration

from pytuber.core.models import PlaylistManager, Provider
from pytuber.storage import Registry


class RegistryParamType(click.ParamType):
    def init_registry(self):
        cfg = os.path.join(click.get_app_dir("pytuber", False), "storage.db")
        Registry.from_file(cfg)


class PlaylistParamType(RegistryParamType):
    name = "ID"

    def complete(self, ctx, incomplete):
        self.init_registry()
        return [
            k
            for k in PlaylistManager.keys()
            if completion_configuration.match_incomplete(k, incomplete)
        ]


class ProviderParamType(click.ParamType):
    name = "Provider"

    def complete(self, ctx, incomplete):
        return [
            k.value
            for k in Provider
            if completion_configuration.match_incomplete(k.value, incomplete)
        ]
