import os
import shutil
import tempfile
import unittest
from unittest import mock

from click.testing import CliRunner

from pytubefm.storage import Registry

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


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
