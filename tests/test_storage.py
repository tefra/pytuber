import json
import os
import shutil
import tempfile
from datetime import timedelta
from unittest import TestCase, mock

from pytuber.storage import Registry


class RegistryTests(TestCase):
    def tearDown(self):
        Registry.clear()
        Registry._obj = {}

    def test_singleton(self):
        a = Registry()
        b = Registry()
        self.assertIs(a, b)

        a[1] = 2
        self.assertEqual({1: 2}, b)

    def test_set(self):
        Registry.set(1, 2, 3, 4, 5)
        self.assertEqual({1: {2: {3: {4: 5}}}}, Registry())

        Registry.set(1, 3, 5)
        self.assertEqual({1: {2: {3: {4: 5}}, 3: 5}}, Registry())

    def test_get(self):
        Registry.set(1, 2, 3, 4, 5)
        self.assertEqual({4: 5}, Registry.get(1, 2, 3))

        with self.assertRaises(KeyError):
            Registry.get(2)

    def test_clear(self):
        Registry.set(1, 2, 3, 4, 5)
        self.assertEqual({4: 5}, Registry.get(1, 2, 3))

        Registry.clear()
        self.assertEqual({}, Registry())

    def test_from_file(self):
        try:
            tmp = tempfile.mkdtemp()
            file_path = os.path.join(tmp, "foo.json")
            with open(file_path, "w") as fp:
                json.dump(dict(a=True), fp)

            Registry.from_file(file_path)

            self.assertEqual(dict(a=True), Registry())

            Registry.set("a", False)

            self.assertFalse(Registry.get("a"))

            Registry.from_file(file_path)
            self.assertFalse(Registry.get("a"))

        finally:
            shutil.rmtree(tmp)

    def test_persist(self):
        try:
            Registry.set(1, 2, 3, 4)
            tmp = tempfile.mkdtemp()
            file_path = os.path.join(tmp, "foo.json")
            Registry.persist(file_path)

            Registry.set(1, 2, 3, 5)
            Registry._obj = {}

            Registry.from_file(file_path)

            self.assertEqual({"1": {"2": {"3": 4}}}, Registry())
        finally:
            shutil.rmtree(tmp)

    @mock.patch("pytuber.storage.time.time")
    def test_cache(self, time):
        time.side_effect = [10, 20.1, 20.1, 20.5, 20.8]

        def callme(ttl, value, refresh=False):
            return Registry.cache(
                key="foo",
                ttl=timedelta(seconds=ttl),
                func=lambda: value,
                refresh=refresh,
            )

        self.assertEqual("first", callme(10, "first"))
        self.assertEqual(("first", 20.0), Registry.get("foo"))

        self.assertEqual("second", callme(1, "second"))
        self.assertEqual(("second", 21.1), Registry.get("foo"))

        self.assertEqual("second", callme(1, "third"))
        self.assertEqual(("second", 21.1), Registry.get("foo"))

        self.assertEqual("third", callme(100, "third", refresh=True))
        self.assertEqual(("third", 120.8), Registry.get("foo"))

        self.assertEqual(5, time.call_count)
