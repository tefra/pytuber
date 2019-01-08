from unittest import mock

from pytubefm.models import Track
from pytubefm.youtube.services import YouService
from tests.utils import TestCase


class YouServiceTests(TestCase):
    @mock.patch.object(YouService, "get_client")
    def test_search(self, get_client):
        client = get_client()
        client.search().list().execute.return_value = {
            "items": [{"id": {"kind": "youtube#video", "videoId": "101"}}]
        }

        track = Track(artist="a", name="b")
        self.assertEqual("101", YouService.search(track))
        client.search().list.assert_has_calls(
            [
                mock.call(),
                mock.call(
                    part="snippet",
                    maxResults=1,
                    q="{} {}".format(track.artist, track.name),
                    type="video",
                ),
            ]
        )
