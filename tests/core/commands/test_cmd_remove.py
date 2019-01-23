from unittest import mock

from pytuber import cli
from pytuber.core.models import PlaylistManager
from tests.utils import CommandTestCase


class CommandRemovePlaylistsTests(CommandTestCase):
    @mock.patch.object(PlaylistManager, "remove")
    def test_remove(self, remove):

        result = self.runner.invoke(cli, ["remove", "foo", "bar"], input="y")

        expected_output = (
            "Do you want to continue? [y/N]: y",
            "Removed playlist: foo!",
            "Removed playlist: bar!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        remove.assert_has_calls([mock.call("foo"), mock.call("bar")])

    def test_remove_no_confirm(self):
        result = self.runner.invoke(cli, ["remove", "foo"], input="n")

        expected_output = ("Do you want to continue? [y/N]: n", "Aborted!")
        self.assertEqual(1, result.exit_code)
        self.assertOutput(expected_output, result.output)
