from unittest import mock

import pydrag

from pytuber import cli
from pytuber.lastfm.services import LastService
from tests.utils import CommandTestCase


class CommandTagsTests(CommandTestCase):
    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_default(self, _, get_tags):
        get_tags.return_value = [
            pydrag.Tag(name="rock", count=1, reach=2),
            pydrag.Tag(name="rap", count=2, reach=4),
            pydrag.Tag(name="metal", count=3, reach=6),
        ]
        result = self.runner.invoke(cli, ["tags"])
        expected_output = (
            "No  Name      Count    Reach",
            "----  ------  -------  -------",
            "   0  rock          1        2",
            "   1  rap           2        4",
            "   2  metal         3        6",
        )

        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        get_tags.assert_called_once_with(refresh=False)

    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_force_refresh(self, _, get_tags):
        result = self.runner.invoke(cli, ["tags", "--refresh"])

        self.assertEqual(0, result.exit_code)
        get_tags.assert_called_once_with(refresh=True)
