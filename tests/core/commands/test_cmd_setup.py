from unittest import mock

from google.oauth2.credentials import Credentials

from pytuber import cli
from pytuber.core.models import ConfigManager, Provider
from pytuber.core.services import YouService
from tests.utils import CommandTestCase


class CommandSetupYoutubeTests(CommandTestCase):
    @mock.patch.object(YouService, "authorize")
    def test_create(self, authorize):
        authorize.return_value = Credentials(
            token="token",
            token_uri="token_uri",
            client_id="client_id",
            client_secret="client_secret",
            scopes="scopes",
        )

        self.assertIsNone(ConfigManager.get(Provider.youtube, default=None))
        client_secrets = "~/Downloads/client_secrets.json"
        result = self.runner.invoke(cli, ["setup", "youtube", client_secrets])

        authorize.assert_called_once_with(client_secrets)
        self.assertEqual(0, result.exit_code)

        expected = {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "quota_limit": 1000000,
            "refresh_token": None,
            "scopes": "scopes",
            "token_uri": "token_uri",
        }
        actual = ConfigManager.get(Provider.youtube)
        self.assertDictEqual(expected, actual.data)

    def test_update(self):
        ConfigManager.set(dict(provider=Provider.youtube, data={"foo": "bar"}))
        client_secrets = "~/Downloads/client_secrets.json"
        result = self.runner.invoke(
            cli,
            ["setup", "youtube", client_secrets, "--quota-limit", 500],
            input="n",
        )

        expected_output = "\n".join(
            ("Overwrite existing configuration? [y/N]: n", "Aborted!")
        )
        self.assertEqual(1, result.exit_code)
        self.assertIn(expected_output, result.output.strip())
