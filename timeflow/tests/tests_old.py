import datetime
import os
import subprocess
import sys
import unittest

from io import StringIO
from unittest import mock

from timeflow import helpers
from timeflow.arg_parser import parse_args


class FakeDateTime(datetime.datetime):
     def __new__(cls, *args, **kwargs):
        return datetime.datetime.__new__(datetime.datetime, *args, **kwargs)


class TestArgParser(unittest.TestCase):
    "Tests if all commands and options work as expected"

    def setUp(self):
        self.test_dir = os.path.dirname(os.path.realpath(__file__))
        self.real_log_file = helpers.LOG_FILE

        # overwrite log file setting, to define file to be used in tests
        helpers.LOG_FILE = self.test_dir + '/fake_log.txt'

    def mock_subprocess(*args, **kwargs):
        return 'mocked'

    def test_log(self):
        "Tests log command"
        # this tests needs separate log file
        helpers.LOG_FILE = self.test_dir + '/auto_fake_log.txt'

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

        # as this test creates separate log file - remove it
        try:
            # if test file is not the same as real log file - remove it
            if helpers.LOG_FILE is not self.real_log_file:
                os.remove(helpers.LOG_FILE)
        except OSError:
            pass

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

    def mock_date_and_stdout(self, args,
                             date_value=datetime.datetime(2015, 1, 1)):
        # mocking example is taken from:
        # https://docs.python.org/3/library/unittest.mock-examples.html
        with mock.patch('timeflow.arg_parser.dt') as dt:
            dt.now.return_value = date_value
            dt.side_effect = lambda *args, **kw: dt(*args, **kw)

            # mock sys.stdout to evalute python's print() output
            sys.stdout = StringIO()
            args = parse_args(args)
            args.func(args)
            return sys.stdout.getvalue().strip()

    def test_stats(self):
        output = self.mock_date_and_stdout(['stats'])
        self.assertEqual(output, "Work: 02h 50min\nSlack: 01h 10min")

    def test_stats_yesterday(self):
        output = self.mock_date_and_stdout(
            ['stats', '--yesterday'],
            date_value=datetime.datetime(2015, 1, 2)
        )
        self.assertEqual(output, "Work: 02h 50min\nSlack: 01h 10min")

        output = self.mock_date_and_stdout(
            ['stats', '-y'],
            date_value=datetime.datetime(2015, 1, 2)
        )
        self.assertEqual(output, "Work: 02h 50min\nSlack: 01h 10min")

    def test_stats_day(self):
        output = self.mock_date_and_stdout(['stats', '--day', '2015-01-01'])
        self.assertEqual(output, "Work: 02h 50min\nSlack: 01h 10min")

        output = self.mock_date_and_stdout(['stats', '-d', '2015-01-01'])
        self.assertEqual(output, "Work: 02h 50min\nSlack: 01h 10min")

    def test_stats_week(self):
        output = self.mock_date_and_stdout(
            ['stats', '--week', '2015-01-02'],
            date_value=datetime.datetime(2015, 2, 5)
        )
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

    @mock.patch('timeflow.helpers.dt', FakeDateTime)
    @mock.patch('timeflow.arg_parser.dt', FakeDateTime)
    def test_stats_last_week(self):
        date_value = datetime.datetime(2015, 1, 5)  # it's monday
        FakeDateTime.now = classmethod(lambda cls: date_value)

        sys.stdout = StringIO()
        args = parse_args(['stats', '--last-week'])
        args.func(args)
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

    def test_stats_month(self):
        output = self.mock_date_and_stdout(
            ['stats', '--month', '1'],
            date_value=datetime.datetime(2015, 1, 5)
        )
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

        output = self.mock_date_and_stdout(
            ['stats', '--month', '2015-1'],
            date_value=datetime.datetime(2015, 1, 5)
        )
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

        output = self.mock_date_and_stdout(
            ['stats', '--month', '2015-01'],
            date_value=datetime.datetime(2015, 1, 5)
        )
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

    @mock.patch('timeflow.helpers.dt', FakeDateTime)
    @mock.patch('timeflow.arg_parser.dt', FakeDateTime)
    def test_stats_last_month(self):
        date_value = datetime.datetime(2015, 2, 5)
        FakeDateTime.now = classmethod(lambda cls: date_value)

        sys.stdout = StringIO()
        args = parse_args(['stats', '--last-month'])
        args.func(args)
        output = sys.stdout.getvalue().strip()
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

    def test_stats_from(self):
        output = self.mock_date_and_stdout(
            ['stats', '--from', '2015-01-02'],
            date_value=datetime.datetime(2015, 1, 5)
        )
        self.assertEqual(output, "Work: 03h 10min\nSlack: 01h 30min")

        output = self.mock_date_and_stdout(
            ['stats', '-f', '2015-01-02'],
            date_value=datetime.datetime(2015, 1, 5)
        )
        self.assertEqual(output, "Work: 03h 10min\nSlack: 01h 30min")

    def test_stats_to(self):
        output = self.mock_date_and_stdout(
            ['stats', '--from', '2015-01-01', '--to', '2015-01-03'],
            date_value=datetime.datetime(2015, 1, 5)
        )
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

        output = self.mock_date_and_stdout(
            ['stats', '-f', '2015-01-01', '-t', '2015-01-02'],
            date_value=datetime.datetime(2015, 1, 5)
        )
        self.assertEqual(output, "Work: 06h 00min\nSlack: 02h 40min")

    def test_stats_report(self):
        output = self.mock_date_and_stdout(['stats', '--report'])
        self.assertEqual(output,
"""Django:
    1h 35min: read documentation
Total: 1h 35min

Timeflow:
    1h 15min: start project
Total: 1h 15min

--------------------------------------------------------------------------------
Breakfast:
    0h 45min
Total: 0h 45min

Slack:
    0h 25min: watch YouTube
Total: 0h 25min

Work: 02h 50min
Slack: 01h 10min""")


if __name__ == "__main__":
    unittest.main()
