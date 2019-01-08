import json
from unittest import mock

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from pytubefm import cli
from pytubefm.models import ConfigManager, Provider, Track, TrackManager
from pytubefm.youtube.models import SCOPES
from pytubefm.youtube.services import YouService
from tests.utils import CommandTestCase, fixture_path


class CommandSetupTests(CommandTestCase):
    @mock.patch.object(InstalledAppFlow, "from_client_config")
    def test_run(self, from_client_config):
        flow = from_client_config()
        flow.run_console.return_value = Credentials(
            token="token",
            token_uri="token_uri",
            client_id="client_id",
            client_secret="client_secret",
            scopes="scopes",
        )

        self.assertIsNone(ConfigManager.get(Provider.youtube))
        client_secrets = fixture_path("client_secret.json")
        result = self.runner.invoke(cli, ["youtube", "setup", client_secrets])

        with open(client_secrets, "r") as f:
            expected = json.load(f)

        from_client_config.assert_has_calls(
            [mock.call(), mock.call(expected, scopes=SCOPES)]
        )
        self.assertEqual(0, result.exit_code)

        expected = {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": None,
            "scopes": "scopes",
            "token_uri": "token_uri",
        }
        actual = ConfigManager.get(Provider.youtube)
        self.assertDictEqual(expected, actual.data)


class CommandMatchTests(CommandTestCase):
    @mock.patch.object(TrackManager, "update")
    @mock.patch.object(YouService, "search")
    @mock.patch.object(TrackManager, "find")
    def test_run(self, find, search, update, *args):
        track_one = Track(artist="a", name="b")
        track_two = Track(artist="c", name="d", youtube_id="y2")
        track_three = Track(artist="e", name="f")
        find.return_value = [track_one, track_two, track_three]

        search.side_effect = ["y1", "y3"]
        result = self.runner.invoke(cli, ["youtube", "match"])

        self.assertEqual(0, result.exit_code)
        self.assertEqual("", result.output.strip())

        search.assert_has_calls([mock.call(track_one), mock.call(track_three)])

        update.assert_has_calls(
            [
                mock.call(track_one, dict(youtube_id="y1")),
                mock.call(track_three, dict(youtube_id="y3")),
            ]
        )
