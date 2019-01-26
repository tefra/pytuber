import click

from pytuber.core.models import PlaylistManager, TrackManager
from pytuber.core.services import YouService
from pytuber.utils import spinner, timestamp


@click.command("youtube")
@click.option("--all", is_flag=True, help="Perform all tasks")
@click.option("--playlists", is_flag=True, help="Create new playlists")
@click.option("--tracks", is_flag=True, help="Update playlist items")
@click.pass_context
def push(
    ctx: click.Context,
    tracks: bool = False,
    playlists: bool = False,
    all: bool = False,
):
    """Update youtube playlists and tracks."""

    if not all and not playlists and not tracks:
        click.secho(ctx.get_help())
        click.Abort()

    if all or playlists:
        push_playlists()
    if all or tracks:
        push_tracks()


def push_playlists():
    playlists = PlaylistManager.find(youtube_id=None)
    message = "Creating playlists"
    with spinner(message) as sp:
        for playlist in playlists:
            sp.text = "{}: {}".format(message, playlist.title)
            youtube_id = YouService.create_playlist(playlist)
            PlaylistManager.update(playlist, dict(youtube_id=youtube_id))

        total = len(playlists)
        if total > 0:
            sp.text = "{0}: {1}/{1} ".format(message, total)


def push_tracks():
    online_playlists = PlaylistManager.find(youtube_id=lambda x: x is not None)
    click.secho("Syncing playlists", bold=True)
    for playlist in online_playlists:
        add = items = remove = []
        with spinner("Fetching playlist items: {}".format(playlist.title)):
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

        message = "Adding new playlist items"
        with spinner(message) as sp:
            for video_id in sorted(add):
                sp.text = "{}: {}".format(message, video_id)
                YouService.create_playlist_item(playlist, video_id)

            if len(add) > 0:
                sp.text = "{}: {}".format(message, len(add))

        message = "Removing playlist items"
        with spinner(message) as sp:
            remove = [item for item in items if item.video_id in remove]
            for item in sorted(remove):
                sp.text = "{}: {}".format(message, video_id)
                YouService.remove_playlist_item(item)

            if len(remove) > 0:
                sp.text = "{}: {}".format(message, len(remove))

        if len(add) or len(remove):
            PlaylistManager.update(playlist, dict(uploaded=timestamp()))
