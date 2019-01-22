from typing import List, Tuple

import click

from pytuber.lastfm.services import LastService
from pytuber.models import PlaylistManager, Provider, TrackManager


@click.command("lastfm")
@click.argument("ids", required=False, nargs=-1)
def fetch_playlists(ids: Tuple[str]):
    """Sync one or more playlists by id, leave empty to sync all."""

    playlists = PlaylistManager.find(provider=Provider.lastfm)
    if ids:
        playlists = list(filter(lambda x: x.id in ids, playlists))

    with click.progressbar(playlists, label="Syncing playlists") as bar:
        for playlist in bar:
            tracklist = LastService.get_tracks(
                type=playlist.type, **playlist.arguments
            )

            track_ids: List[str] = []
            for entry in tracklist:
                id = TrackManager.set(
                    dict(artist=entry.artist.name, name=entry.name)
                ).id

                if id not in track_ids:
                    track_ids.append(id)

            PlaylistManager.update(playlist, dict(tracks=track_ids))