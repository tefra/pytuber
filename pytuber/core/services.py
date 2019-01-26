from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from pytuber.core.models import (
    ConfigManager,
    Playlist,
    PlaylistItem,
    Provider,
    Track,
)


class YouService:
    max_results = 50
    client = None
    scopes = ["https://www.googleapis.com/auth/youtube"]

    @classmethod
    def authorize(cls, client_secrets):
        return InstalledAppFlow.from_client_secrets_file(
            client_secrets, scopes=cls.scopes
        ).run_console()

    @classmethod
    def search_track(cls, track: Track):
        params = dict(
            part="snippet",
            maxResults=1,
            q="{} {}".format(track.artist, track.name),
            type="video",
        )

        response = cls.get_client().search().list(**params).execute()
        for item in response.get("items", []):
            if item["id"]["kind"] == "youtube#video":
                return item["id"]["videoId"]

    @classmethod
    def get_playlists(cls):
        params = dict(part="snippet", mine=True, maxResults=cls.max_results)
        next_page_token = None
        playlists = []
        while True:
            if next_page_token:
                params.update(dict(pageToken=next_page_token))

            response = cls.get_client().playlists().list(**params).execute()
            for item in response.get("items", []):
                playlist = Playlist.from_mime(
                    item["snippet"]["description"].strip().split("\n")[-1]
                )
                if playlist:
                    if playlist.title != item["snippet"]["title"]:
                        playlist.title = item["snippet"]["title"]
                    playlist.youtube_id = item["id"]
                    playlists.append(playlist)

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return playlists

    @classmethod
    def create_playlist(cls, playlist: Playlist):
        params = dict(
            body=dict(
                snippet=dict(title=playlist.title, description=playlist.mime),
                status=dict(privacyStatus="private"),
            ),
            part="snippet,status",
        )
        return cls.get_client().playlists().insert(**params).execute()["id"]

    @classmethod
    def get_playlist_items(cls, playlist: Playlist):
        items = []
        next_page_token = None
        params = dict(
            part="contentDetails,snippet",
            maxResults=cls.max_results,
            playlistId=playlist.youtube_id,
        )
        while True:
            if next_page_token:
                params.update(dict(pageToken=next_page_token))

            resp = cls.get_client().playlistItems().list(**params).execute()
            for item in resp.get("items", []):

                try:
                    artist, name = item["snippet"]["title"].split("-", 1)
                except ValueError:
                    artist = ""
                    name = item["snippet"]["title"]

                items.append(
                    PlaylistItem(
                        id=item["id"],
                        video_id=item["contentDetails"]["videoId"],
                        artist=artist.strip(),
                        name=name.strip(),
                    )
                )

            next_page_token = resp.get("nextPageToken")
            if not next_page_token:
                break
        return items

    @classmethod
    def create_playlist_item(cls, playlist: Playlist, video_id):
        params = dict(
            body=dict(
                snippet=dict(
                    playlistId=playlist.youtube_id,
                    resourceId=dict(kind="youtube#video", videoId=video_id),
                )
            ),
            part="snippet",
        )
        return cls.get_client().playlistItems().insert(**params).execute()

    @classmethod
    def remove_playlist_item(cls, playlist_item: PlaylistItem):
        params = dict(id=playlist_item.id)
        return cls.get_client().playlistItems().delete(**params).execute()

    @classmethod
    def get_client(cls):
        if not cls.client:
            info = ConfigManager.get(Provider.youtube).data
            credentials = Credentials.from_authorized_user_info(
                info, scopes=cls.scopes
            )
            cls.client = build("youtube", "v3", credentials=credentials)
        return cls.client
