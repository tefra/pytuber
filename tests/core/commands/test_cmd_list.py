from unittest import mock

from pytuber import cli
from pytuber.core.models import PlaylistManager
from tests.utils import CommandTestCase, PlaylistFixture


class CommandListPlaylistsTests(CommandTestCase):
    @mock.patch.object(PlaylistManager, "find")
    def test_list_playlists(self, find):
        find.return_value = PlaylistFixture.get(
            2,
            youtube_id=["456ybnm", None],
            synced=[None, 1546727285],
            uploaded=[None, 1546727385],
            tracks=[[], list(range(0, 99))],
        )
        result = self.runner.invoke(cli, ["list"])

        expected_output = (
            "ID    Title    Provider     Youtube     Tracks",
            "----  -------  ----------  ---------  --------",
            "id_a  title_a  provider_a      ✔             0",
            "id_b  title_b  provider_b      -            99",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        find.assert_called_once_with()

    @mock.patch.object(PlaylistManager, "find")
    def test_list_playlists_with_provider(self, find):
        result = self.runner.invoke(cli, ["list", "--provider", "foo"])
        self.assertEqual(0, result.exit_code)
        find.assert_called_once_with(provider="foo")
