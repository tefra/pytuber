import contextlib
from datetime import datetime

import click
from yaspin import yaspin


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


def date(timestamp: int):
    if not timestamp:
        return "-"
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
