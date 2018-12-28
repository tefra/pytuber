import os

from click.testing import CliRunner

from pytubefm import cli
from pytubefm.models import Config, Provider
from tests.utils import TestCase


class CommandsTests(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandsTests, self).setUp()

    def test_setup_with_new_config(self):
        self.assertIsNone(Config.find_by_provider(Provider.lastfm))
        result = self.runner.invoke(cli, ["lastfm", "setup"], input="aaaa")

        expected_output = os.linesep.join(
            ("Last.fm Api Key: aaaa", "Last.fm configuration updated!")
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

        actual = Config.find_by_provider(Provider.lastfm)
        self.assertDictEqual({"api_key": "aaaa"}, actual.data)

    def test_setup_overwrites_existing_config(self):
        Config(
            provider=Provider.lastfm.value, data=dict(api_key="bbbb")
        ).save()

        self.assertEqual(
            dict(api_key="bbbb"), Config.find_by_provider(Provider.lastfm).data
        )
        result = self.runner.invoke(
            cli, ["lastfm", "setup"], input=os.linesep.join(("aaaa", "y"))
        )

        expected_output = os.linesep.join(
            (
                "Last.fm Api Key: aaaa",
                "Overwrite existing configuration? [y/N]: y",
                "Last.fm configuration updated!",
            )
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

        actual = Config.find_by_provider(Provider.lastfm)
        self.assertDictEqual({"api_key": "aaaa"}, actual.data)
