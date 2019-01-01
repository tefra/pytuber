import os
import unittest

from click.testing import CliRunner

from pytubefm.models import Storage

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


class TestCase(unittest.TestCase):
    def setUp(self):
        Storage().data = dict()
        self.maxDiff = None
        super(TestCase, self).setUp()


class CommandTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandTestCase, self).setUp()
