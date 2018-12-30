from pytubefm.models import PlaylistType


class UserPlaylist(PlaylistType):
    LOVED_TRACKS = "user_loved_tracks"
    TOP_TRACKS = "user_top_tracks"
    RECENT_TRACKS = "user_recent_tracks"
    FRIENDS_RECENT_TRACKS = "user_friends_recent_tracks"


class ChartPlaylist(PlaylistType):
    CHART = "top_tracks"
    COUNTRY = "top_tracks_by_country"
    TAG = "top_tracks_by_tag"
    ARTIST = "top_tracks_by_artist"
