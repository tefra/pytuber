import json
import os

from click.testing import CliRunner

import pytubefm
from tests.utils import TestCase, fixture_path


class CommandsTests(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandsTests, self).setUp()

    def test_setup_with_new_config(self):
        self.assertIsNone(self.obj.get_config(pytubefm.YOUTUBE))
        client_secrets = fixture_path("client_secret.json")
        result = self.runner.invoke(
            pytubefm.cli,
            ["youtube", "setup"],
            input=client_secrets,
            obj=self.obj,
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
        actual = self.obj.get_config(pytubefm.YOUTUBE)
        self.assertDictEqual(expected, actual["data"])

    def test_setup_overwrites_existing_config(self):
        self.obj.update_config(pytubefm.YOUTUBE, "foo")
        self.assertEqual("foo", self.obj.get_config(pytubefm.YOUTUBE)["data"])
        client_secrets = fixture_path("client_secret.json")
        result = self.runner.invoke(
            pytubefm.cli,
            ["youtube", "setup"],
            input=os.linesep.join((client_secrets, "y")),
            obj=self.obj,
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

        actual = self.obj.get_config(pytubefm.YOUTUBE)
        self.assertDictEqual(expected, actual["data"])
