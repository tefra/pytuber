import os
import shutil
import tempfile
import unittest

import pickledb

from pytubefm.models import Document

here = os.path.abspath(os.path.dirname(__file__))


def fixture_path(filename):
    return os.path.join(here, "fixtures", filename)


class TestCase(unittest.TestCase):
    def setUp(self):
        Document.db = pickledb.load(
            os.path.join(tempfile.mkdtemp(), "storage.db"), True
        )
        super(TestCase, self).setUp()

    def tearDown(self):
        try:
            shutil.rmtree(Document.db.loco)
        except (OSError, IOError):
            pass
        finally:
            Document.db = None
        super(TestCase, self).tearDown()
