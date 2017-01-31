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
    email_time_range = None
    literal_time_range = ''
    if args.yesterday:
        yesterday_obj = dt.datetime.now() - dt.timedelta(days=1)
        date_from = date_to = yesterday_obj.strftime(utils.DATE_FORMAT)
        email_time_range = "day"
    elif args.day:
        date_from = date_to = args.day
        email_time_range = "day"
    elif args.week:
        date_from, date_to = utils.get_week_range(args.week)
        literal_time_range = "this week"
        email_time_range = "week"
    elif args.this_week:
        date_from, date_to = utils.get_this_week()
        literal_time_range = "this week"
        email_time_range = "week"
    elif args.last_week:
        date_from, date_to = utils.get_last_week()
        literal_time_range = "this week"
        email_time_range = "week"
    elif args.month:
        date_from, date_to = utils.get_month_range(args.month)
        literal_time_range = "this month"
        email_time_range = "month"
    elif args.this_month:
        date_from, date_to = utils.get_this_month()
        literal_time_range = "this month"
        email_time_range = "month"
    elif args.last_month:
        date_from, date_to = utils.get_last_month()
        literal_time_range = "this month"
        email_time_range = "month"
    elif args._from and not args.to:
        date_from = args._from
        date_to = dt.datetime.now().strftime(utils.DATE_FORMAT)
    elif args._from and args.to:
        date_from = args._from
        date_to = args.to
    else:
        # default action is to show today's  stats
        date_from = date_to = dt.datetime.now().strftime(utils.DATE_FORMAT)
        email_time_range = "day"
        today = True

    if args.report or args.report_as_gtimelog:
        work_report, slack_report = statistics.calculate_report(
            utils.read_log_file_lines(),
            date_from,
            date_to
        )
        if args.report:
            output = statistics.create_full_report(work_report, slack_report)
        elif args.report_as_gtimelog:
            output = statistics.create_report_as_gtimelog(
                work_report,
                literal_time_range=literal_time_range,
            )

        print(output)

        if args.email:
            statistics.email_report(date_from, date_to, output,
                                    email_time_range=email_time_range)

    # do not print current working time if it's a report
    if not any((args.report, args.report_as_gtimelog)):
        work_time, slack_time, today_work_time = statistics.calculate_stats(
            utils.read_log_file_lines(), date_from, date_to, today=today
        )
        print(statistics.get_total_stats_times(work_time, slack_time, today_work_time))


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
    stats_parser.add_argument(
        "--email",
        action="store_true",
        help="Send generated report to activity email"
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
