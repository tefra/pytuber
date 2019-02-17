from unittest import mock

from pytuber import cli
from pytuber.core.commands.cmd_add import (
    create_playlist,
    parse_jspf,
    parse_m3u,
    parse_text,
    parse_xspf,
)
from pytuber.core.models import PlaylistManager, PlaylistType, Provider
from tests.utils import CommandTestCase, PlaylistFixture


class CommandAddTests(CommandTestCase):
    @mock.patch("click.edit")
    @mock.patch("pytuber.core.commands.cmd_add.create_playlist")
    @mock.patch("pytuber.core.commands.cmd_add.parse_text")
    def test_add_from_editor(self, parse_text, create_playlist, clk_edit):
        clk_edit.return_value = "foo"
        parse_text.return_value = ["a", "b"]
        self.runner.invoke(
            cli, ["add", "editor", "--title", "My Cool Playlist"]
        )
        parse_text.assert_called_once_with("foo")
        create_playlist.assert_called_once_with(
            arguments={"_title": "My Cool Playlist"},
            title="My Cool Playlist",
            tracks=["a", "b"],
            type=PlaylistType.EDITOR,
        )

    @mock.patch("pytuber.core.commands.cmd_add.parse_m3u")
    @mock.patch("pytuber.core.commands.cmd_add.parse_xspf")
    @mock.patch("pytuber.core.commands.cmd_add.parse_jspf")
    @mock.patch("pytuber.core.commands.cmd_add.parse_text")
    @mock.patch("pytuber.core.commands.cmd_add.create_playlist")
    def test_add_from_file(self, create_playlist, *args):
        text, jspf, xspf, m3u = args
        text.return_value = list("txt")
        jspf.return_value = list("jspf")
        xspf.return_value = list("xspf")
        m3u.return_value = list("m3u")

        with self.runner.isolated_filesystem():
            for format in ["txt", "jspf", "xspf", "m3u"]:
                with open("hello.{}".format(format), "w") as f:
                    f.write(format)

                self.runner.invoke(
                    cli,
                    [
                        "add",
                        "file",
                        "hello.{}".format(format),
                        "--title",
                        "Mew",
                        "--format",
                        format,
                    ],
                )

            jspf.assert_called_once_with("jspf")
            xspf.assert_called_once_with("xspf")
            text.assert_called_once_with("txt")
            m3u.assert_called_once_with("m3u")

            create_playlist.assert_has_calls(
                [
                    mock.call(
                        arguments={"_file": "hello.txt"},
                        title="Mew",
                        tracks=list("txt"),
                        type=PlaylistType.FILE,
                    ),
                    mock.call(
                        arguments={"_file": "hello.jspf"},
                        title="Mew",
                        tracks=list("jspf"),
                        type=PlaylistType.FILE,
                    ),
                    mock.call(
                        arguments={"_file": "hello.xspf"},
                        title="Mew",
                        tracks=list("xspf"),
                        type=PlaylistType.FILE,
                    ),
                    mock.call(
                        arguments={"_file": "hello.m3u"},
                        title="Mew",
                        tracks=list("m3u"),
                        type=PlaylistType.FILE,
                    ),
                ]
            )


class CommandAddUtilsTests(CommandTestCase):
    def test_parse_text(self):
        text = "\n".join(
            (
                "Queen - Bohemian Rhapsody",
                " Queen - Bohemian Rhapsody",
                "Queen -I want to break free",
                " # a - b",
                " ",
                "Wrong Format",
            )
        )
        expected = [
            ("Queen", "Bohemian Rhapsody"),
            ("Queen", "I want to break free"),
        ]
        self.assertEqual(expected, parse_text(text))

    def test_parse_xspf(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
            <playlist version="1" xmlns="http://xspf.org/ns/0/">
                <trackList>
                    <track>
                        <creator>Queen</creator>
                        <title>Bohemian Rhapsody</title>
                    </track>
                    <track>
                        <creator>Queen</creator>
                        <title>Bohemian Rhapsody</title>
                    </track>
                    <track>
                        <creator>Queen</creator>
                        <title>I want to break free</title>
                    </track>
                    <track>
                        <creator>No track</creator>
                    </track>
                    <track>
                        <title>No artist</title>
                    </track>
                </trackList>
            </playlist>"""

        expected = [
            ("Queen", "Bohemian Rhapsody"),
            ("Queen", "I want to break free"),
        ]
        self.assertEqual(expected, parse_xspf(xml))
        self.assertEqual([], parse_xspf(""))

    def test_parse_jspf(self):
        json = """
        {
          "playlist": {
            "title": "Two Songs From Thriller",
            "creator": "MJ Fan",
            "track": [
              {
                "title": "Bohemian Rhapsody",
                "creator": "Queen"
              },
              {
                "title": "Bohemian Rhapsody",
                "creator": "Queen"
              },
              {
                "creator": "Queen"
              },
              {
                "title": "Bohemian Rhapsody"
              },
              {
                "title": "I want to break free",
                "creator": "Queen"
              }
            ]
          }
        }"""

        expected = [
            ("Queen", "Bohemian Rhapsody"),
            ("Queen", "I want to break free"),
        ]
        self.assertEqual(expected, parse_jspf(json))
        self.assertEqual([], parse_jspf(""))

    def test_parse_m3u(self):
        text = "\n".join(
            (
                "#EXTM3U",
                "#EXTINF:123, Queen - Bohemian Rhapsody",
                "#EXTINF:123, Queen - Bohemian Rhapsody",
                "#EXTINF:123,Queen - I want to break free",
                "#EXTINF:123 whatever format 1",
                "#EXTINF:123, whatever format 2",
            )
        )
        expected = [
            ("Queen", "Bohemian Rhapsody"),
            ("Queen", "I want to break free"),
        ]
        self.assertEqual(expected, parse_m3u(text))
        self.assertEqual([], parse_m3u(""))

    @mock.patch("pytuber.core.commands.cmd_add.magenta")
    @mock.patch.object(PlaylistManager, "set")
    @mock.patch("click.confirm")
    @mock.patch("click.secho")
    @mock.patch("click.clear")
    def test_create_playlist(self, clear, secho, confirm, set, magenta):
        magenta.side_effect = lambda x: x
        set.return_value = PlaylistFixture.one()
        tracks = [
            ("Queen", "Bohemian Rhapsody"),
            ("Queen", "I want to break free"),
        ]
        create_playlist(
            title="My Cool Playlist",
            tracks=tracks,
            type="foo",
            arguments=dict(foo="bar"),
        )

        expected_ouput = (
            "Title:  My Cool Playlist",
            "Tracks:  2",
            "",
            "  No  Artist    Track Name",
            "----  --------  --------------------",
            "   1  Queen     Bohemian Rhapsody",
            "   2  Queen     I want to break free",
        )

        self.assertOutput(expected_ouput, secho.call_args_list[0][0][0])
        self.assertEqual(
            "Added playlist: id_a!", secho.call_args_list[1][0][0]
        )

        clear.assert_called_once_with()
        confirm.assert_called_once_with(
            "Are you sure you want to save this playlist?", abort=True
        )
        set.assert_called_once_with(
            dict(
                type="foo",
                arguments=dict(foo="bar"),
                provider=Provider.user,
                title="My Cool Playlist",
                tracks=["55a4d2b", "b045fee"],
            )
        )

    @mock.patch("click.secho")
    def test_create_playlist_empty_tracks(self, secho):
        create_playlist(title="foo", tracks=[], type=None, arguments=None)
        secho.assert_called_once_with("Tracklist is empty, aborting...")
