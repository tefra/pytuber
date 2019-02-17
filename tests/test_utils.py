from unittest import TestCase, mock
from unittest.mock import PropertyMock

from pytuber.utils import date, spinner


class UtilsTests(TestCase):
    def test_date(self):
        self.assertEqual("-", date(None))
        self.assertEqual("-", date(0))
        self.assertEqual("2019-02-17 09:02", date(1550394167))

    @mock.patch("pytuber.utils.yaspin")
    def test_spinner(self, yaspin):
        type(yaspin.return_value).green = PropertyMock(return_value=yaspin)
        with spinner("foo") as sp:
            self.assertEqual(sp, yaspin.return_value)

        yaspin.return_value.start.assert_called_once_with()
        yaspin.return_value.stop.assert_called_once_with()

    @mock.patch("click.secho")
    @mock.patch("pytuber.utils.yaspin")
    def test_spinner_with_exception(self, yaspin, secho):
        type(yaspin.return_value).green = PropertyMock(return_value=yaspin)
        with spinner("foo"):
            raise Exception("Fatal")

        yaspin.return_value.start.assert_called_once_with()
        yaspin.return_value.stop.assert_called_once_with()
        secho.assert_called_once_with("Fatal")
