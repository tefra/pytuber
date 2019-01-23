from pytuber import cli
from pytuber.core.models import ConfigManager, Provider
from tests.utils import CommandTestCase


class CommandSetupLastfmTests(CommandTestCase):
    def test_create(self):
        self.assertIsNone(ConfigManager.get(Provider.lastfm, default=None))
        result = self.runner.invoke(cli, ["setup", "lastfm"], input="aaaa")

        expected_output = (
            "Last.fm Api Key: aaaa",
            "Last.fm configuration updated!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)

        actual = ConfigManager.get(Provider.lastfm)
        self.assertDictEqual({"api_key": "aaaa"}, actual.data)

    def test_update(self):
        ConfigManager.set(
            dict(provider=Provider.lastfm, data=dict(api_key="bbbb"))
        )

        self.assertEqual(
            dict(api_key="bbbb"), ConfigManager.get(Provider.lastfm).data
        )
        result = self.runner.invoke(
            cli, ["setup", "lastfm"], input="\n".join(("aaaa", "y"))
        )

        expected_output = (
            "Last.fm Api Key: aaaa",
            "Overwrite existing configuration? [y/N]: y",
            "Last.fm configuration updated!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)

        actual = ConfigManager.get(Provider.lastfm)
        self.assertDictEqual({"api_key": "aaaa"}, actual.data)
