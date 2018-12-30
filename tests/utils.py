import os
import shutil
import tempfile
import unittest

import pickledb
from click.testing import CliRunner

from pytubefm.models import Storage

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


class TestCase(unittest.TestCase):
    def setUp(self):
        Storage.db = pickledb.load(
            os.path.join(tempfile.mkdtemp(), "storage.db"), False
        )
        self.maxDiff = None
        super(TestCase, self).setUp()

    def tearDown(self):
        try:
            shutil.rmtree(Storage.db.loco)
        except (OSError, IOError):
            pass
        finally:
            Storage.db = None
        super(TestCase, self).tearDown()


class CommandTestCase(TestCase):
    def setUp(self):
        self.runner = CliRunner()
        super(CommandTestCase, self).setUp()
