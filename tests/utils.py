import os
import unittest

from click.testing import CliRunner

from pytubefm.data import Registry

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


class TestCase(unittest.TestCase):
    def setUp(self):
        Registry().clear()
        self.maxDiff = None
        super(TestCase, self).setUp()


class CommandTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandTestCase, self).setUp()
