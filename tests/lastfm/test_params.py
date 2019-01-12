from collections import namedtuple
from unittest import TestCase, mock
from unittest.mock import call

import click
from click import BadParameter
from pydrag import Artist, Tag

from pytuber.lastfm.params import (
    ArtistParamType,
    CountryParamType,
    TagParamType,
    UserParamType,
)
from pytuber.lastfm.services import LastService


class CountryParamTypeTests(TestCase):
    def setUp(self):
        self.param = CountryParamType()
        super(CountryParamTypeTests, self).setUp()

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
        super(TagParamTypeTests, self).setUp()

    def test_type(self):
        self.assertEqual("Tag", self.param.name)
        self.assertIsInstance(self.param, click.ParamType)

    @mock.patch.object(LastService, "get_tags")
    def test_convert_successful(self, get_tags):
        rap = Tag(name="Rap")
        rock = Tag(name="Rock")
        get_tags.return_value = [rap, rock]
        self.assertEqual("Rock", self.param.convert("rock", None, None))
        self.assertEqual("Rap", self.param.convert("RaP", None, None))
        get_tags.assert_has_calls([call(), call()])

    @mock.patch.object(LastService, "get_tags")
    def test_convert_error(self, get_tags):
        get_tags.return_value = []
        with self.assertRaises(BadParameter) as cm:
            self.param.convert("rock", None, None)

        msg = "Unknown tag: rock"
        self.assertEqual(msg, str(cm.exception))


class ArtistParamTypeTests(TestCase):
    def setUp(self):
        self.param = ArtistParamType()
        super(ArtistParamTypeTests, self).setUp()

    def test_type(self):
        self.assertEqual("Artist", self.param.name)
        self.assertIsInstance(self.param, click.ParamType)

    @mock.patch.object(LastService, "get_artist")
    def test_convert_successful(self, get_artist):
        get_artist.return_value = Artist(name="Queen")

        self.assertEqual("Queen", self.param.convert("queen", None, None))
        get_artist.assert_called_once_with("queen")

    @mock.patch.object(LastService, "get_artist")
    def test_convert_error(self, get_artist):
        get_artist.side_effect = Exception("Who died")
        with self.assertRaises(BadParameter) as cm:
            self.param.convert("queen", None, None)

        msg = "Unknown artist: queen"
        self.assertEqual(msg, str(cm.exception))


class UserParamTypeTests(TestCase):
    def setUp(self):
        self.param = UserParamType()
        super(UserParamTypeTests, self).setUp()

    def test_type(self):
        self.assertEqual("User", self.param.name)
        self.assertIsInstance(self.param, click.ParamType)

    @mock.patch.object(LastService, "get_user")
    def test_convert_successful(self, get_user):
        user = namedtuple("User", ["name"])
        get_user.return_value = user(name="Rj")

        self.assertEqual("Rj", self.param.convert("rj", None, None))
        get_user.assert_called_once_with("rj")

    @mock.patch.object(LastService, "get_user")
    def test_convert_error(self, get_user):
        get_user.side_effect = Exception("Who died")
        with self.assertRaises(BadParameter) as cm:
            self.param.convert("rj", None, None)

        msg = "Unknown user: rj"
        self.assertEqual(msg, str(cm.exception))
