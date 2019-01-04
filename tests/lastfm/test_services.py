from datetime import timedelta
from unittest import mock
from unittest.mock import call

import click
from click import Abort
from pydrag import Artist, Tag

from pytubefm.data import Registry
from pytubefm.lastfm.services import LastService
from pytubefm.models import Config, Provider
from tests.utils import TestCase


class LastServiceTests(TestCase):
    @mock.patch.object(LastService, "assert_config")
    @mock.patch("pytubefm.data.time.time")
    @mock.patch.object(Tag, "get_top_tags")
    def test_get_tags(self, get_top_tags, time, assert_config):
        time.return_value = 1

        get_top_tags.side_effect = [
            [Tag(name=i) for i in range(0, 250)],
            [Tag(name=i) for i in range(250, 500)],
            [Tag(name=i) for i in range(500, 750)],
            [Tag(name=i) for i in range(750, 1000)],
        ]

        names = [t.name for t in LastService.get_tags()]
        self.assertEqual(list(range(0, 1000)), names)

        get_top_tags.assert_has_calls(
            [
                call(limit=250, page=1),
                call(limit=250, page=2),
                call(limit=250, page=3),
                call(limit=250, page=4),
            ]
        )

        tags, ttl = Registry.get("last.fm_tag_list")
        self.assertEqual(1000, len(tags))
        self.assertEqual({"name": 0}, tags[0])
        self.assertEqual(timedelta(days=30, seconds=1).total_seconds(), ttl)
        assert_config.assert_called_once()

    @mock.patch.object(LastService, "assert_config")
    @mock.patch("pytubefm.data.time.time")
    @mock.patch.object(Artist, "find")
    def test_get_artist(self, find, time, assert_config):
        time.return_value = 1

        find.return_value = Artist(name="Queen")

        artist = LastService.get_artist("quueee")
        self.assertEqual(Artist(name="Queen"), artist)

        find.assert_called_once_with("quueee")

        artist, ttl = Registry.get("last.fm_artist_quueee")
        self.assertEqual({"name": "Queen"}, artist)

        self.assertEqual(timedelta(days=30, seconds=1).total_seconds(), ttl)
        assert_config.assert_called_once()

    @mock.patch("pytubefm.lastfm.services.configure")
    @mock.patch.object(click, "secho")
    def test_assert_config(self, secho, configure):
        with self.assertRaises(Abort):
            LastService.assert_config()
        secho.assert_called_once_with(
            "Run setup to configure last.fm services"
        )

        Config(provider=Provider.lastfm, data=dict(api_key="aaa")).save()
        LastService.assert_config()
        configure.assert_called_once_with(api_key="aaa")
