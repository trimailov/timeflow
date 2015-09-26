import os
import shutil
import subprocess
import unittest

from unittest import mock

from timeflow import helpers
from timeflow.arg_parser import parse_args


class TestParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(
            os.path.realpath(__file__)
        ) + '/test_dir/'

        self.real_log_file = helpers.LOG_FILE

        # overwrite log file setting, to define file to be used in tests
        helpers.LOG_FILE = self.test_dir + '/test_log'

    def tearDown(self):
        try:
            # if test file is not the same as real log file - remove it
            if helpers.LOG_FILE is not self.real_log_file:
                shutil.rmtree(self.test_dir)
        except OSError:
            pass

    def mock_subprocess(*args, **kwargs):
        return 'mocked'

    def test_log(self):
        args = parse_args(['log', 'loging message'])
        args.func(args)
        self.assertEqual(len(helpers.read_log_file_lines()), 1)
        # get message without datetime string and colon sign at the end of it
        msg_line = helpers.read_log_file_lines()[0]
        msg = msg_line[helpers.DATETIME_LEN+1:]
        self.assertEqual(msg, ' loging message\n')

        args = parse_args(['log', 'second loging message'])
        args.func(args)
        self.assertEqual(len(helpers.read_log_file_lines()), 2)
        # get message without datetime string and colon sign at the end of it
        msg_line = helpers.read_log_file_lines()[1]
        msg = msg_line[helpers.DATETIME_LEN+1:]
        self.assertEqual(msg, ' second loging message\n')

    def test_edit(self):
        subprocess.call = self.mock_subprocess
        with mock.patch.dict('os.environ', {'EDITOR': 'vim'}):
            args = parse_args(['edit'])
            args.func(args)

        with mock.patch.dict('os.environ', {'EDITOR': ''}):
            args = parse_args(['edit'])
            args.func(args)

    def test_edit_e(self):
        subprocess.call = self.mock_subprocess
        args = parse_args(['edit', '-e', 'vim'])
        args.func(args)

    def test_edit_editor(self):
        args = parse_args(['edit', '--editor', 'vim'])

    def test_stats(self):
        args = parse_args(['stats'])

    def test_stats_today(self):
        args = parse_args(['stats', '--today'])

    def test_stats_yesterday(self):
        args = parse_args(['stats', '--yesterday'])

    def test_stats_day(self):
        args = parse_args(['stats', '--day', '2015-01-01'])

    def test_stats_week(self):
        args = parse_args(['stats', '--week', '2015-01-01'])

    def test_stats_last_week(self):
        args = parse_args(['stats', '--last-week'])

    def test_stats_month(self):
        args = parse_args(['stats', '--month', '2015-01-01'])

    def test_stats_last_month(self):
        args = parse_args(['stats', '--last-month'])

    def test_stats_from(self):
        args = parse_args(['stats', '--from', '2015-01-01'])

    def test_stats_to(self):
        args = parse_args(['stats', '--to', '2015-01-01'])


if __name__ == "__main__":
    unittest.main()
