import os

import appdirs
import click
from tinydb import Query, TinyDB


class Context(object):
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = appdirs.user_config_dir("pytubefm", False)

        self.config_dir = config_dir
        self.db = TinyDB(os.path.join(config_dir, "data"), create_dirs=True)

    def get_config(self, type):
        return self.db.table("config").get(Query().type == type)

    def update_config(self, type, data):
        self.db.table("config").upsert(
            dict(type=type, data=data), Query().type == type
        )


pass_context = click.make_pass_decorator(Context, ensure=True)
