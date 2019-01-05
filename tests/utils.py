import os
import shutil
import tempfile
import unittest
from unittest import mock

import click
from click.testing import CliRunner

from pytubefm.data import Registry

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


class TestCase(unittest.TestCase):
    @mock.patch.object(click, "get_app_dir")
    def setUp(self, get_app_dir):
        self.tmp_dir = tempfile.mkdtemp()
        get_app_dir.return_value = self.tmp_dir
        self.maxDiff = None
        super(TestCase, self).setUp()

    def tearDown(self):
        Registry().clear()
        shutil.rmtree(self.tmp_dir)
        super(TestCase, self).tearDown()


class CommandTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandTestCase, self).setUp()
