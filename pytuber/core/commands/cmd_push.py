import click

from pytuber.models import PlaylistManager, TrackManager
from pytuber.utils import spinner
from pytuber.youtube.services import YouService


@click.group("youtube")
def youtube_push():
    """Last.fm is a music service that learns what you love."""


@youtube_push.command("playlists")
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


@youtube_push.command("tracks")
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
