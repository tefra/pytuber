import click

from pytuber.core.models import PlaylistManager
from pytuber.core.params import PlaylistParamType
from pytuber.core.params import ProviderParamType
from pytuber.core.params import RegistryParamType
from tests.utils import PlaylistFixture
from tests.utils import TestCase


class PlaylistParamTypeTests(TestCase):
    def setUp(self):
        self.param = PlaylistParamType()
        super().setUp()

    def test_type(self):
        self.assertEqual("ID", self.param.name)
        self.assertIsInstance(self.param, RegistryParamType)

    def test_complete(self):
        [PlaylistManager.set(p.asdict()) for p in PlaylistFixture.get(2)]

        self.assertEqual(["id_a", "id_b"], self.param.complete(None, ""))
        self.assertEqual(["id_a"], self.param.complete(None, "id_a"))


class ProviderParamTypeTests(TestCase):
    def setUp(self):
        self.param = ProviderParamType()
        super().setUp()

    def test_type(self):
        self.assertEqual("Provider", self.param.name)
        self.assertIsInstance(self.param, click.ParamType)

    def test_complete(self):
        self.assertEqual(["last.fm", "youtube", "user"], self.param.complete(None, ""))
        self.assertEqual(["youtube"], self.param.complete(None, "you"))
