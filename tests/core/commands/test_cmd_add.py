from unittest import mock

from pytuber import cli
from pytuber.core.models import PlaylistManager, PlaylistType, Provider
from tests.utils import CommandTestCase, PlaylistFixture


class CommandEditorTests(CommandTestCase):
    @mock.patch("click.edit")
    @mock.patch.object(PlaylistManager, "set")
    def test_successful(self, create_playlist, click_edit):
        click_edit.return_value = "\n".join(
            (
                "Queen - Bohemian Rhapsody",
                " Queen - Bohemian Rhapsody",
                "Queen -I want to break free",
                "#" " ",
                "Wrong Format",
            )
        )

        create_playlist.return_value = PlaylistFixture.one()
        result = self.runner.invoke(
            cli,
            ["add", "editor", "--title", "My Cool Playlist"],
            input="\n".join(("y",)),
            catch_exceptions=False,
        )

        expected_output = (
            "Title:  My Cool Playlist",
            "Tracks:  2",
            "",
            "  No  Artist    Track Name",
            "----  --------  --------------------",
            "   1  Queen     Bohemian Rhapsody",
            "   2  Queen     I want to break free",
            "",
            "Are you sure you want to save this playlist? [y/N]: y",
            "Added playlist: id_a!",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        create_playlist.assert_called_once_with(
            dict(
                type=PlaylistType.EDITOR,
                provider=Provider.user,
                title="My Cool Playlist",
                tracks=["55a4d2b", "b045fee"],
            )
        )

    @mock.patch("click.edit")
    @mock.patch.object(PlaylistManager, "set")
    def test_aborted(self, create_playlist, click_edit):
        click_edit.return_value = None

        result = self.runner.invoke(
            cli,
            ["add", "editor", "--title", "My Cool Playlist"],
            input="\n".join(("y",)),
            catch_exceptions=False,
        )

        expected_output = ("Aborted!",)
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
        self.assertEqual(0, create_playlist.call_count)
