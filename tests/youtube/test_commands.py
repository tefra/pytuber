import json
import os

from click.testing import CliRunner

from pytubefm import cli
from pytubefm.models import Config, Provider
from tests.utils import TestCase, fixture_path


class CommandsTests(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandsTests, self).setUp()

    def test_setup_with_new_config(self):
        self.assertIsNone(Config.find_by_provider(Provider.youtube))
        client_secrets = fixture_path("client_secret.json")
        result = self.runner.invoke(
            cli, ["youtube", "setup"], input=client_secrets
        )

        expected_output = os.linesep.join(
            (
                "Credentials file path: {}".format(client_secrets),
                "Youtube configuration updated!",
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

        with open(client_secrets, "r") as f:
            expected = json.load(f)
        actual = Config.find_by_provider(Provider.youtube)
        self.assertDictEqual(expected, actual.data)

    def test_setup_overwrites_existing_config(self):
        Config(provider=Provider.youtube.value, data=dict(a=1)).save()
        self.assertEqual(
            dict(a=1), Config.find_by_provider(Provider.youtube).data
        )
        client_secrets = fixture_path("client_secret.json")
        result = self.runner.invoke(
            cli,
            ["youtube", "setup"],
            input=os.linesep.join((client_secrets, "y")),
        )

        expected_output = os.linesep.join(
            (
                "Credentials file path: {}".format(client_secrets),
                "Overwrite existing configuration? [y/N]: y",
                "Youtube configuration updated!",
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

        with open(client_secrets, "r") as f:
            expected = json.load(f)

        actual = Config.find_by_provider(Provider.youtube)
        self.assertDictEqual(expected, actual.data)
