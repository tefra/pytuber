import click
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from pytubefm.models import ConfigManager, Provider, Track
from pytubefm.youtube.models import SCOPES


class YouService:
    client = None

    @classmethod
    def search(cls, track: Track):
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
    def get_client(cls):
        if not cls.client:
            try:
                info = ConfigManager.get(Provider.youtube).data
                credentials = Credentials.from_authorized_user_info(
                    info, scopes=SCOPES
                )
            except (KeyError, AttributeError):
                click.secho("Run setup to configure youtube services")
                raise click.Abort()
            cls.client = build("youtube", "v3", credentials=credentials)
        return cls.client
