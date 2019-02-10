import shutil
import tempfile
import unittest
from unittest import mock

from click.testing import CliRunner

from pytuber.core.models import (
    ConfigManager,
    Playlist,
    PlaylistItem,
    Provider,
    Track,
)
from pytuber.storage import Registry


class TestCase(unittest.TestCase):
    def setUp(self):
        tmp_dir = tempfile.mkdtemp()

        get_app_dir_patch = mock.patch("click.get_app_dir")
        get_app_dir = get_app_dir_patch.start()
        get_app_dir.return_value = tmp_dir
        self.addCleanup(get_app_dir_patch.stop)
        self.addCleanup(lambda: shutil.rmtree(tmp_dir))

        self.maxDiff = None
        super(TestCase, self).setUp()

    def tearDown(self):
        Registry().clear()
        super(TestCase, self).tearDown()


class CommandTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandTestCase, self).setUp()

    def assertOutput(self, messages, output):
        self.assertEqual("\n".join(messages), output.strip())

    def assertOutputContains(self, messages, output):
        for i, text in enumerate(output.strip().split("\n")):
            try:
                message = messages[i]
            except IndexError:
                message = ""
            self.assertIn(message, text)


class Fixture:
    @classmethod
    def one(cls, num=0, **kwargs):
        letter = chr(97 + num)
        data = cls.generate(letter=letter, num=num, **kwargs)
        return cls.model(**data)

    @classmethod
    def get(cls, num, **kwargs):
        res = []
        for i in range(0, num):
            params = {k: v[i] for k, v in kwargs.items()}
            res.append(cls.one(num=i, **params))
        return res


class TrackFixture(Fixture):
    model = Track

    @classmethod
    def generate(cls, letter, num, **kwargs):
        params = dict(
            id="id_%s" % letter,
            name="name_%s" % letter,
            artist="artist_%s" % letter,
        )
        params.update(kwargs)
        return params


class PlaylistFixture(Fixture):
    model = Playlist

    @classmethod
    def generate(cls, letter, num, **kwargs):
        params = dict(
            id="id_%s" % letter,
            title="title_%s" % letter,
            type="type_%s" % letter,
            provider="provider_%s" % letter,
            arguments={letter: num},
        )
        params.update(kwargs)
        return params


class PlaylistItemFixture(Fixture):
    model = PlaylistItem

    @classmethod
    def generate(cls, letter, num, **kwargs):
        params = dict(
            id="id_%s" % letter,
            name="name_%s" % letter,
            artist="artist_%s" % letter,
            video_id="video_id_%s" % letter,
        )
        params.update(kwargs)
        return params


class ConfigFixture:
    @classmethod
    def youtube(cls):
        ConfigManager.set(
            dict(
                provider=Provider.youtube.value,
                data=dict(
                    refresh_token=None,
                    token_uri=None,
                    client_id=None,
                    client_secret=None,
                    scopes=None,
                    quota_limit=100,
                ),
            )
        )
