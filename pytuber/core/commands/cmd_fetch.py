import click

from pytuber.models import PlaylistManager, TrackManager
from pytuber.utils import spinner
from pytuber.youtube.services import YouService


@click.group("youtube")
def youtube_fetch():
    """Last.fm is a music service that learns what you love."""


@youtube_fetch.command("playlists")
def fetch_playlists():
    """Fetch remote information and update local playlists."""
    with spinner("Fetching playlists information") as sp:
        for playlist in YouService.get_playlists():
            PlaylistManager.set(playlist.asdict())
            sp.write("Imported playlist {}".format(playlist.id))


@youtube_fetch.command("tracks")
def fetch_tracks():
    """Match local tracks to youtube videos."""

    tracks = TrackManager.find(youtube_id=None)
    if len(tracks) == 0:
        return click.secho("There are no new tracks")

    click.secho("Fetching tracks information", bold=True)
    for track in tracks:
        with spinner("Track: {} - {}".format(track.artist, track.name)):
            youtube_id = YouService.search_track(track)
            TrackManager.update(track, dict(youtube_id=youtube_id))
