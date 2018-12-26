import os
import shutil
import tempfile
import unittest

from pytubefm.main import Context

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


class TestCase(unittest.TestCase):
    def setUp(self):
        self.obj = Context(config_dir=tempfile.mkdtemp())
        super(TestCase, self).setUp()

    def tearDown(self):
        self.obj.db.close()

        try:
            shutil.rmtree(self.obj.config_dir)
        except (OSError, IOError):
            pass

        super(TestCase, self).tearDown()
