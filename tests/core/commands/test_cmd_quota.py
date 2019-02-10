from datetime import datetime
from unittest import mock

from pytuber import cli
from pytuber.core.services import YouService
from tests.utils import CommandTestCase, ConfigFixture


class CommandQuotaTests(CommandTestCase):
    @mock.patch.object(YouService, "get_quota_usage")
    @mock.patch.object(YouService, "quota_date")
    def test_run(self, quota_date, get_quota_usage):
        ConfigFixture.youtube()
        get_quota_usage.return_value = 9988
        quota_date.return_value = datetime(
            year=1970, month=1, day=1, hour=22, minute=22, second=11
        )
        result = self.runner.invoke(cli, ["quota"])

        expected_output = (
            "Provider:  youtube",
            "     Limit:  1000000",
            "     Usage:  9988",
            "Next reset:  1:37:49",
        )
        self.assertEqual(0, result.exit_code)
        self.assertOutput(expected_output, result.output)
