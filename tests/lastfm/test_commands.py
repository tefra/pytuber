import os

from click.testing import CliRunner

import pytubefm
from tests.utils import TestCase


class CommandsTests(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandsTests, self).setUp()

    def test_setup_with_new_config(self):
        self.assertIsNone(self.obj.get_config(pytubefm.LASTFM))
        result = self.runner.invoke(
            pytubefm.cli, ["lastfm", "setup"], input="aaaa", obj=self.obj
        )

        expected_output = os.linesep.join(
            ("Last.fm Api Key: aaaa", "Last.fm configuration updated!")
        )
        self.assertEqual(0, result.exit_code)
        self.assertEqual(expected_output, result.output.strip())

        actual = self.obj.get_config(pytubefm.LASTFM)
        self.assertDictEqual({"api_key": "aaaa"}, actual["data"])

    def test_setup_overwrites_existing_config(self):
        self.obj.update_config(pytubefm.LASTFM, "foo")
        self.assertEqual("foo", self.obj.get_config(pytubefm.LASTFM)["data"])
        result = self.runner.invoke(
            pytubefm.cli,
            ["lastfm", "setup"],
            input=os.linesep.join(("aaaa", "y")),
            obj=self.obj,
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

        actual = self.obj.get_config(pytubefm.LASTFM)
        self.assertDictEqual({"api_key": "aaaa"}, actual["data"])
