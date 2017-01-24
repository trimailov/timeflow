import datetime as dt
import os
import sys
import subprocess

from argparse import ArgumentParser

from timeflow import stats as statistics
from timeflow import utils


def log(args):
    utils.write_to_log_file(args.message)


def _call_editor(editor, filename):
    editor = editor.split()
    subprocess.call(editor + [utils.LOG_FILE])


def edit(args):
    if args.editor:
        _call_editor(args.editor, utils.LOG_FILE)
    else:
        subprocess.call(['echo', 'Trying to open $EDITOR'])
        if os.environ.get('EDITOR'):
            _call_editor(os.environ.get('EDITOR'), utils.LOG_FILE)
        else:
            subprocess.call([
                "echo",
                "Set your default editor in EDITOR environment variable or \n"
                "call edit command with -e option and pass your editor:\n"
                "timeflow edit -e vim",
            ])


def stats(args):
    today = False
    date_from = date_to = None
    if args.yesterday:
        yesterday_obj = dt.datetime.now() - dt.timedelta(days=1)
        date_from = date_to = yesterday_obj.strftime(utils.DATE_FORMAT)
    elif args.day:
        date_from = date_to = args.day
    elif args.week:
        date_from, date_to = utils.get_week_range(args.week)
    elif args.this_week:
        date_from, date_to = utils.get_this_week()
    elif args.last_week:
        date_from, date_to = utils.get_last_week()
    elif args.month:
        date_from, date_to = utils.get_month_range(args.month)
    elif args.this_month:
        date_from, date_to = utils.get_this_month()
    elif args.last_month:
        date_from, date_to = utils.get_last_month()
    elif args._from and not args.to:
        date_from = args._from
        date_to = dt.datetime.now().strftime(utils.DATE_FORMAT)
    elif args._from and args.to:
        date_from = args._from
        date_to = args.to
    else:
        # default action is to show today's  stats
        date_from = date_to = dt.datetime.now().strftime(utils.DATE_FORMAT)
        today = True

    if args.report or args.report_as_gtimelog:
        work_report, slack_report = statistics.calculate_report(
            statistics.read_log_file_lines(),
            date_from,
            date_to
        )
        if args.report:
            print(statistics.create_full_report(work_report, slack_report))
        elif args.report_as_gtimelog:
            print(statistics.create_report_as_gtimelog(work_report))

    # do not print current working time if it's a report
    if not any((args.report, args.report_as_gtimelog)):
        work_time, slack_time, today_work_time = statistics.calculate_stats(
            statistics.read_log_file_lines(), date_from, date_to, today=today
        )
        statistics.print_stats(work_time, slack_time, today_work_time)


def create_parser():
    parser = ArgumentParser()
    subparser = parser.add_subparsers()

    # `log` command
    log_parser = subparser.add_parser(
        "log",
        help="Log your time and explanation for it",
    )
    log_parser.add_argument(
        "message",
        help="The message which explains your spent time",
    )
    log_parser.set_defaults(func=log)

    # `edit` command
    edit_parser = subparser.add_parser(
        "edit",
        help="Open editor to fix/edit the time log",
    )
    edit_parser.add_argument("-e", "--editor", help="Use some editor")
    edit_parser.set_defaults(func=edit)

    # `stats` command
    stats_parser = subparser.add_parser(
        "stats",
        help="Show how much time was spent working or slacking"
    )
    stats_parser.add_argument(
        "--today",
        action="store_true",
        help="Show today's work times (default)"
    )
    stats_parser.add_argument(
        "-y", "--yesterday",
        action="store_true",
        help="Show yesterday's work times"
    )
    stats_parser.add_argument(
        "-d", "--day",
        help="Show specific day's work times"
    )
    stats_parser.add_argument(
        "--week",
        help="Show specific week's work times"
    )
    stats_parser.add_argument(
        "--this-week",
        action="store_true",
        help="Show current week's work times"
    )
    stats_parser.add_argument(
        "--last-week",
        action="store_true",
        help="Show last week's work times"
    )
    stats_parser.add_argument(
        "--month",
        help="Show specific month's work times"
    )
    stats_parser.add_argument(
        "--this-month",
        action="store_true",
        help="Show current month's work times"
    )
    stats_parser.add_argument(
        "--last-month",
        action="store_true",
        help="Show last month's work times"
    )
    stats_parser.add_argument(
        "-f", "--from",
        help="Show work times from specific date",
        dest="_from"
    )
    stats_parser.add_argument(
        "-t", "--to",
        help="Show work times from to specific date"
    )
    stats_parser.add_argument(
        "-r", "--report",
        action="store_true",
        help="Show stats in report form"
    )
    stats_parser.add_argument(
        "--report-as-gtimelog",
        action="store_true",
        help="Show stats in gtimelog report form"
    )
    stats_parser.set_defaults(func=stats)

    # pass every argument to parser, except the program name
    return parser


def cli():
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    # if nothing is passed - print help
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
