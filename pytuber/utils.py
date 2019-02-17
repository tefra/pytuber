import contextlib
from datetime import datetime
from typing import Optional

import click
from yaspin import yaspin

from pytuber.storage import Registry


def magenta(text):
    return click.style(str(text), fg="magenta")


@contextlib.contextmanager
def spinner(text):
    sp = yaspin(text=text)
    sp.start()
    try:
        yield sp
        sp.green.ok("✔")
    except Exception as e:
        sp.red.fail("✘")
        click.secho(str(e))
    finally:
        sp.stop()


def timestamp():
    return int(datetime.utcnow().strftime("%s"))


def date(timestamp: Optional[int] = None):
    if not timestamp:
        return "-"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def init_registry(path: str, version: str):
    Registry.from_file(path)

    current_version = Registry.get("version", default="0")
    if current_version == "0":
        if Registry.exists("configuration", "youtube", "data"):
            Registry.set(
                "configuration", "youtube", "data", "quota_limit", 1000000
            )

    Registry.set("version", version)
