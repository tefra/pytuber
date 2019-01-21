import attr


@attr.s(auto_attribs=True)
class PlaylistItem:
    id: str
    video_id: str
