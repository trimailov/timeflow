import datetime
import os

import pytest

import timeflow.utils
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
    timeflow.utils.LOG_FILE = tmp_path

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
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run edit command
    parser = cli.create_parser()
    args = parser.parse_args(['edit'])
    args.func(args)


def test_stats_now(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 2 hours 50 min\n"
              "Slack: 1 hour 10 min\n"
              "\n"
              "Today working for: 15 hours 59 min\n")
    assert out == result


def test_stats_yesterday(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--yesterday'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 2 hours 50 min\n"
              "Slack: 1 hour 10 min\n")
    assert out == result


def test_stats_day(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--day', '2015-01-01'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 2 hours 50 min\n"
              "Slack: 1 hour 10 min\n")
    assert out == result


def test_stats_this_week(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--this-week'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 8 hours 50 min\n"
              "Slack: 3 hours 50 min\n")
    assert out == result


def test_stats_last_week(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--last-week'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 2 hours 50 min\n"
              "Slack: 1 hour 10 min\n")
    assert out == result


def test_stats_week(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--week', '2015-01-01'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 8 hours 50 min\n"
              "Slack: 3 hours 50 min\n")
    assert out == result


def test_stats_last_month(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--last-month'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 5 hours 40 min\n"
              "Slack: 2 hours 20 min\n")
    assert out == result


def test_stats_this_month(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--this-month'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 2 hours 50 min\n"
              "Slack: 1 hour 10 min\n")
    assert out == result


def test_stats_month(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--month', '1'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 6 hours\n"
              "Slack: 2 hours 40 min\n")
    assert out == result


def test_stats_from(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--from', '2014-12-28'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 5 hours 40 min\n"
              "Slack: 2 hours 20 min\n")
    assert out == result


def test_stats_from_to(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--from', '2014-12-24',
                              '--to', '2015-01-01'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = ("Work: 8 hours 30 min\n"
              "Slack: 3 hours 30 min\n")
    assert out == result


def test_stats_now_report(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--report'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = (
        "------------------------------ WORK -------------------------------\n"
        "Django:\n"
        "    1 hour 35 min: read documentation\n"
        "    Total: 1 hour 35 min\n"
        "\n"
        "Timeflow:\n"
        "    1 hour 15 min: start project\n"
        "    Total: 1 hour 15 min\n"
        "------------------------------ SLACK ------------------------------\n"
        "Breakfast:\n"
        "    0 hours 45 min: Breakfast\n"
        "    Total: 0 hours 45 min\n"
        "\n"
        "Slack:\n"
        "    0 hours 25 min: watch YouTube\n"
        "    Total: 0 hours 25 min\n"
    )
    assert out == result


def test_stats_now_report_as_gtimelog(patch_datetime_now, capsys):
    test_dir = os.path.dirname(os.path.realpath(__file__))

    # overwrite log file setting, to define file to be used in tests
    timeflow.utils.LOG_FILE = test_dir + '/fake_log.txt'

    # run stats command
    parser = cli.create_parser()
    args = parser.parse_args(['stats', '--report-as-gtimelog'])
    args.func(args)

    # extract STDOUT, as stats command prints to it
    out, err = capsys.readouterr()
    result = (
        "                                                                time\n"
        "Django: read documentation                                      1 hour 35 min\n"
        "Timeflow: start project                                         1 hour 15 min"
        "\n"
        "\n"
        "Total work done this month: 2 hours 50 min"
        "\n"
        "\n"
        "By category:"
        "\n"
        "\n"
        "Django                                                          1 hour 35 min\n"
        "Timeflow                                                        1 hour 15 min\n\n"
    )
    assert out == result
