import click

from pytuber.core.models import StrEnum


class PlaylistMixin(StrEnum):
    @classmethod
    def choices(cls):
        prompts = ["Playlist Types"]
        prompts.extend(
            [
                "[{}] {}".format(i + 1, x.value.replace("_", " ").title())
                for i, x in enumerate(cls)
            ]
        )
        prompts.extend(["Select a playlist type 1-{}".format(len(cls))])
        return "\n".join(prompts)

    @classmethod
    def from_choice(cls, choice: int) -> "PlaylistMixin":
        return list(cls)[choice - 1]

    @classmethod
    def range(cls):
        return click.IntRange(1, len(cls))


class PlaylistType(PlaylistMixin):
    USER_LOVED_TRACKS = "user_loved_tracks"
    USER_TOP_TRACKS = "user_top_tracks"
    USER_RECENT_TRACKS = "user_recent_tracks"
    USER_FRIENDS_RECENT_TRACKS = "user_friends_recent_tracks"

    CHART = "top_tracks"
    COUNTRY = "top_tracks_by_country"
    TAG = "top_tracks_by_tag"
    ARTIST = "top_tracks_by_artist"


UserPlaylistType = PlaylistMixin(  # type: ignore
    "UserPlaylistType",
    [
        (x.name, x.value)
        for x in [
            PlaylistType.USER_LOVED_TRACKS,
            PlaylistType.USER_TOP_TRACKS,
            PlaylistType.USER_RECENT_TRACKS,
            PlaylistType.USER_FRIENDS_RECENT_TRACKS,
        ]
    ],
)
