from unittest import mock

from pytuber import cli
from tests.utils import CommandTestCase


class CommandAutoCompleteTests(CommandTestCase):
    @mock.patch("click.secho")
    @mock.patch("click_completion.core.install")
    def test_add_from_editor(self, install, secho):
        install.return_value = "foo", "bar"
        self.runner.invoke(cli, ["setup", "autocomplete"])

        install.assert_called_once_with(
            append=True,
            extra_env={
                "_CLICK_COMPLETION_COMMAND_CASE_INSENSITIVE_COMPLETE": "ON"
            },
            shell=None,
        )
        secho.assert_called_once_with("foo completion installed in bar")
