import os

import click
from click_completion import completion_configuration

from pytuber.core.models import PlaylistManager, Provider
from pytuber.utils import init_registry
from pytuber.version import version


class PlaylistParamType(click.ParamType):
    name = "ID"

    def complete(self, ctx, incomplete):
        cfg = os.path.join(click.get_app_dir("pytuber", False), "storage.db")
        init_registry(cfg, version)

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
