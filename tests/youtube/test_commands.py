import json
from unittest import mock

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from pytubefm import cli
from pytubefm.models import ConfigManager, Provider
from pytubefm.youtube.models import SCOPES
from tests.utils import CommandTestCase, fixture_path


class CommandsTests(CommandTestCase):
    @mock.patch.object(InstalledAppFlow, "from_client_config")
    def test_setup_with_new_config(self, from_client_config):
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
