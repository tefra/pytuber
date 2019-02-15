import contextlib
import io
import json
from functools import partial
from typing import List

import click
from lxml import etree
from tabulate import tabulate

from pytuber.core.models import (
    PlaylistManager,
    PlaylistType,
    Provider,
    TrackManager,
)
from pytuber.utils import magenta

option_title = partial(
    click.option, "--title", help="title", type=click.STRING, prompt="Title"
)


@click.command("editor")
@option_title()
def add_from_editor(title: str) -> None:
    """Create playlist in a text editor."""
    marker = (
        "\n\n# Copy/Paste your track list and hit save!\n"
        "# One line per track, make sure it doesn't start with a #\n"
        "# Separate the track artist and title with a single dash `-`\n"
    )
    text = click.edit(marker)
    create_playlist(
        title=title,
        tracks=parse_text(text or ""),
        type=PlaylistType.EDITOR,
        arguments=dict(_title=title.strip()),
    )


@click.command("file")
@click.argument("file", type=click.Path(), required=True)
@click.option(
    "--format",
    type=click.Choice(["txt", "m3u", "xspf", "jspf"]),
    default="txt",
)
@option_title()
def add_from_file(file: str, title: str, format: str) -> None:
    """Import a playlist from a text file."""

    with open(file, "r", encoding="UTF-8") as fp:
        text = fp.read()

    parsers = dict(
        m3u=parse_m3u, jspf=parse_jspf, xspf=parse_xspf, txt=parse_text
    )
    create_playlist(
        title=title,
        tracks=parsers[format](text or ""),
        type=PlaylistType.FILE,
        arguments=dict(_file=file),
    )


def parse_text(text):
    """
    Parse raw text format playlists, each line must contain a single.

    track with artist and title separated by a single dash. eg Queen - Bohemian Rhapsody

    :param str text:
    :return: A list of tracks
    """
    tracks: List[tuple] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split("-", 1)
        if len(parts) != 2:
            continue

        artist, track = list(map(str.strip, parts))
        if not artist or not track or (artist, track) in tracks:
            continue

        tracks.append((artist, track))

    return tracks


def parse_xspf(text):
    """
    XSPF parser.

    :param str text:
    :return: A list of tracks
    """
    tracks = []
    with contextlib.suppress(etree.XMLSyntaxError):
        context = etree.iterparse(io.BytesIO(text.encode("UTF-8")))
        for action, elem in context:
            if elem.tag.endswith("creator"):
                artist = elem.text.strip()
            elif elem.tag.endswith("title"):
                track = elem.text.strip()
            elif elem.tag.endswith("track"):
                if artist and track and (artist, track) not in tracks:
                    tracks.append((artist, track))
                artist = track = None
    return tracks


def parse_jspf(text):
    """
    JSPF parser.

    :param str text:
    :return: A list of tracks
    """

    tracks = []
    with contextlib.suppress(KeyError, json.JSONDecodeError):
        data = json.loads(text)
        for item in data["playlist"]["track"]:
            artist = item.get("creator", "").strip()
            track = item.get("title", "").strip()
            if artist and track and (artist, track) not in tracks:
                tracks.append((artist, track))

    return tracks


def parse_m3u(text):
    """
    M3U parser.

    :param str text:
    :return: A list of tracks
    """

    tracks: List[tuple] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("#EXTINF:"):
            continue

        parts = line.split(",", 1)
        if len(parts) != 2:
            continue

        parts = parts[1].split("-", 1)
        if len(parts) != 2:
            continue

        artist, track = list(map(str.strip, parts))
        if not artist or not track or (artist, track) in tracks:
            continue

        tracks.append((artist, track))

    return tracks


def create_playlist(title, tracks, type, arguments):
    if not tracks:
        return click.secho("Tracklist is empty, aborting...")

    click.clear()
    click.secho(
        "{}\n\n{}\n".format(
            tabulate(  # type: ignore
                [
                    (magenta("Title:"), title),
                    (magenta("Tracks:"), len(tracks)),
                ],
                tablefmt="plain",
                colalign=("right", "left"),
            ),
            tabulate(  # type: ignore
                [
                    (i + 1, track[0], track[1])
                    for i, track in enumerate(tracks)
                ],
                headers=("No", "Artist", "Track Name"),
            ),
        )
    )
    click.confirm("Are you sure you want to save this playlist?", abort=True)
    playlist = PlaylistManager.set(
        dict(
            type=type,
            title=title.strip(),
            arguments=arguments,
            provider=Provider.user,
            tracks=[
                TrackManager.set(dict(artist=artist, name=name)).id
                for artist, name in tracks
            ],
        )
    )
    click.secho("Added playlist: {}!".format(playlist.id))
