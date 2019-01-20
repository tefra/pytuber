import click

from pytuber.models import PlaylistManager, TrackManager
from pytuber.utils import spinner
from pytuber.youtube.services import YouService


@click.group("youtube")
def youtube():
    pass


@youtube.command()
def purge():
    """Cleanup youtube related data from playlists and tracks."""

    for playlist in PlaylistManager.find():
        if playlist.youtube_id:
            PlaylistManager.update(playlist, dict(youtube_id=None))

    for track in TrackManager.find():
        if track.youtube_id:
            TrackManager.update(track, dict(youtube_id=None))


@youtube.group()
def push():
    """Push local playlists and tracks to youtube."""


@youtube.group()
def fetch():
    """Fetch playlist and tracks information from youtube."""


@fetch.command("playlists")
def fetch_playlists():
    """Fetch remote information and update local playlists."""
    with spinner("Fetching playlists information") as sp:
        for playlist in YouService.get_playlists():
            PlaylistManager.set(playlist.asdict())
            sp.write("Imported playlist {}".format(playlist.id))


@fetch.command("tracks")
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


@push.command("playlists")
def push_playlists():
    """Create new playlists on youtube."""

    playlists = PlaylistManager.find(youtube_id=None)
    if len(playlists) == 0:
        return click.secho("There are no new playlists")

    click.secho("Creating playlists", bold=True)
    for playlist in playlists:
        with spinner("Playlist: {}".format(playlist.display_type)):
            youtube_id = YouService.create_playlist(playlist)
            PlaylistManager.update(playlist, dict(youtube_id=youtube_id))


@push.command("tracks")
def push_tracks():
    online_playlists = PlaylistManager.find(youtube_id=lambda x: x is not None)
    click.secho("Syncing playlists", bold=True)
    for playlist in online_playlists:
        add = items = remove = []
        with spinner(
            "Fetching playlist items: {}".format(playlist.display_type)
        ):
            items = YouService.get_playlist_items(playlist)
            online = set([item.video_id for item in items])
            offline = set(
                [
                    track.youtube_id
                    for track in TrackManager.find(
                        youtube_id=lambda x: x is not None,
                        id=lambda x: x in playlist.tracks,
                    )
                ]
            )

            add = offline - online
            remove = online - offline

        if len(add) == len(remove) == 0:
            click.secho("Playlist is already synced!")
            continue

        if len(add) > 0:
            click.secho("Adding new playlist items", bold=True)
            for video_id in sorted(add):
                with spinner("Adding video: {}".format(video_id)):
                    YouService.create_playlist_item(playlist, video_id)

        if len(remove) > 0:
            click.secho("Removing playlist items", bold=True)
            remove = [item for item in items if item.video_id in remove]
            for item in sorted(remove):
                with spinner("Removing video: {}".format(item.video_id)):
                    YouService.remove_playlist_item(item)
