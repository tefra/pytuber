import os
import shutil
import tempfile
import unittest

from tinydb import TinyDB

from pytubefm.models import Document

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


class TestCase(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        Document.db = TinyDB(
            os.path.join(self.tmp_dir, "data"), create_dirs=True
        )
        super(TestCase, self).setUp()

    def tearDown(self):
        Document.db.close()
        Document.db = None

        try:
            shutil.rmtree(self.tmp_dir)
        except (OSError, IOError):
            pass

        super(TestCase, self).tearDown()
