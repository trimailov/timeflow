import datetime
import os

import pytest

import timeflow
from timeflow import cli

FAKE_TIME = datetime.datetime(2015, 1, 1, 23, 59, 59)


@pytest.fixture
def patch_datetime_now(monkeypatch):

    class mydatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, 'datetime', mydatetime)


def test_patch_datetime(patch_datetime_now):
    assert datetime.datetime.now() == FAKE_TIME


def test_log(patch_datetime_now, tmpdir, capsys):
    tmp_path = tmpdir.join("test_log.txt").strpath
    timeflow.LOG_FILE = tmp_path

    # run log command
    parser = cli.create_parser()
    args = parser.parse_args(['log', 'message'])
    args.func(args)

    with open(tmp_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1
        assert lines[0] == '2015-01-01 23:59: message\n'


def test_edit(patch_datetime_now, tmpdir, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run edit command
    parser = cli.create_parser()
    args = parser.parse_args(['edit'])
    args.func(args)


def test_stats_now(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 02h 50min\n"
              "Slack: 01h 10min\n"
              "\n"
              "Today working for: 15h 59min\n")
    assert result == out


def test_stats_yesterday(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--yesterday'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 02h 50min\n"
              "Slack: 01h 10min\n")
    assert result == out


def test_stats_day(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--day', '2015-01-01'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 02h 50min\n"
              "Slack: 01h 10min\n")
    assert result == out


def test_stats_last_week(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--last-week'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 02h 50min\n"
              "Slack: 01h 10min\n")
    assert result == out


def test_stats_week(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--week', '2015-01-01'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 08h 50min\n"
              "Slack: 03h 50min\n")
    assert result == out


def test_stats_last_month(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--last-month'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 05h 40min\n"
              "Slack: 02h 20min\n")
    assert result == out


def test_stats_month(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--month', '1'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 06h 00min\n"
              "Slack: 02h 40min\n")
    assert result == out


def test_stats_from(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--from', '2014-12-28'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 05h 40min\n"
              "Slack: 02h 20min\n")
    assert result == out


def test_stats_from_to(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--from', '2014-12-24',
                              '--to', '2015-01-01'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 08h 30min\n"
              "Slack: 03h 30min\n")
    assert result == out


def test_stats_now_report(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--report'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = (
        "------------------------------ WORK -------------------------------\n"
        "Django:\n"
        "    1h 35min: read documentation\n"
        "    Total: 1h 35min\n"
        "\n"
        "Timeflow:\n"
        "    1h 15min: start project\n"
        "    Total: 1h 15min\n"
        "\n"
        "------------------------------ SLACK ------------------------------\n"
        "Breakfast:\n"
        "    0h 45min\n"
        "    Total: 0h 45min\n"
        "\n"
        "Slack:\n"
        "    0h 25min: watch YouTube\n"
        "    Total: 0h 25min\n"
        "\n"
        "Work: 02h 50min\n"
        "Slack: 01h 10min\n"
        "\n"
        "Today working for: 15h 59min\n"
    )
    assert result == out
