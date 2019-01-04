from unittest import mock
from unittest.mock import call

import click
from click import BadParameter
from pydrag import Artist, Tag

from pytubefm.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
)
from pytubefm.lastfm.services import LastService
from tests.utils import TestCase


class CountryParamTypeTests(TestCase):
    def setUp(self):
        self.param = CountryParamType()

    def test_type(self):
        self.assertEqual("Country Code", self.param.name)
        self.assertIsInstance(self.param, click.ParamType)

    def test_convert_successful(self):
        self.assertEqual("greece", self.param.convert("gr", None, None))

    def test_convert_error(self):
        with self.assertRaises(BadParameter) as cm:
            self.param.convert("--", None, None)

        msg = "Unknown iso-3166 country code: --"
        self.assertEqual(msg, str(cm.exception))


class TagParamTypeTests(TestCase):
    def setUp(self):
        self.param = TagParamType()

    def test_type(self):
        self.assertEqual("Tag", self.param.name)
        self.assertIsInstance(self.param, click.ParamType)

    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_convert_successful(self, _, get_tags):
        rap = Tag(name="Rap")
        rock = Tag(name="Rock")
        get_tags.return_value = [rap, rock]
        self.assertEqual(rock, self.param.convert("rock", None, None))
        self.assertEqual(rap, self.param.convert("RaP", None, None))
        get_tags.assert_has_calls([call(), call()])

    @mock.patch.object(LastService, "get_tags")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_convert_error(self, _, get_tags):
        get_tags.return_value = []
        with self.assertRaises(BadParameter) as cm:
            self.param.convert("rock", None, None)

        msg = "Unknown tag: rock"
        self.assertEqual(msg, str(cm.exception))


class ArtistParamTypeTests(TestCase):
    def setUp(self):
        self.param = ArtistParamType()

    def test_type(self):
        self.assertEqual("Artist", self.param.name)
        self.assertIsInstance(self.param, click.ParamType)

    @mock.patch.object(LastService, "get_artist")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_convert_successful(self, _, get_artist):
        artist = Artist(name="Queen")
        get_artist.return_value = Artist(name="Queen")

        self.assertEqual(artist, self.param.convert("queen", None, None))
        get_artist.assert_called_once_with("queen")

    @mock.patch.object(LastService, "get_artist")
    @mock.patch.object(LastService, "__init__", return_value=None)
    def test_convert_error(self, _, get_artist):
        get_artist.side_effect = Exception("Who died")
        with self.assertRaises(BadParameter) as cm:
            self.param.convert("queen", None, None)

        msg = "Unknown artist: queen"
        self.assertEqual(msg, str(cm.exception))
