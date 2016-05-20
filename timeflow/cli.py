import datetime as dt
import os
import sys
import subprocess

from argparse import ArgumentParser

import timeflow


def log(args):
    timeflow.write_to_log_file(args.message)


def edit(args):
    if args.editor:
        subprocess.call([args.editor, timeflow.LOG_FILE])
    else:
        subprocess.call(['echo', 'Trying to open $EDITOR'])
        if os.environ.get('EDITOR'):
            subprocess.call([os.environ.get('EDITOR'), timeflow.LOG_FILE])
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
        date_from = date_to = yesterday_obj.strftime(timeflow.DATE_FORMAT)
    elif args.day:
        date_from = date_to = args.day
    elif args.week:
        date_from, date_to = timeflow.get_week_range(args.week)
    elif args.this_week:
        date_from, date_to = timeflow.get_this_week()
    elif args.last_week:
        date_from,  date_to = timeflow.get_last_week()
    elif args.month:
        date_from,  date_to = timeflow.get_month_range(args.month)
    elif args.this_month:
        date_from, date_to = timeflow.get_this_month()
    elif args.last_month:
        date_from,  date_to = timeflow.get_last_month()
    elif args._from and not args.to:
        date_from = args._from
        date_to = dt.datetime.now().strftime(timeflow.DATE_FORMAT)
    elif args._from and args.to:
        date_from = args._from
        date_to = args.to
    else:
        # default action is to show today's  stats
        date_from = date_to = dt.datetime.now().strftime(timeflow.DATE_FORMAT)
        today = True

    if args.report:
        work_report, slack_report = timeflow.calculate_report(
            timeflow.read_log_file_lines(),
            date_from,
            date_to
        )
        timeflow.print_report(work_report, slack_report)

    work_time, slack_time, today_work_time = timeflow.calculate_stats(
        timeflow.read_log_file_lines(), date_from, date_to, today=today
    )
    timeflow.print_stats(work_time, slack_time, today_work_time)


def create_parser():
    parser = ArgumentParser()
    subparser = parser.add_subparsers()

    # `log` command
    log_parser = subparser.add_parser("log")
    log_parser.add_argument("message")
    log_parser.set_defaults(func=log)

    # `edit` command
    edit_parser = subparser.add_parser("edit")
    edit_parser.add_argument("-e", "--editor", help="Explicitly set editor")
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
