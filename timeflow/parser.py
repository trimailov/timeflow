import argparse
from timeflow.helpers import write_to_log_file


def log(args):
    write_to_log_file(args.message)


def edit(args):
    print("Parsing edit command")
    if args.editor:
        print("Parsing edit's --editor option")


def stats(args):
    print("Parsing stats command")
    if args.today:
        print("Parsing stats's --today option")
    elif args.yesterday:
        print("Parsing stats's --yesterday option")
    elif args.day:
        print("Parsing stats's --day option")
    elif args.week:
        print("Parsing stats's --week option")
    elif args.last_week:
        print("Parsing stats's --last-week option")
    elif args.month:
        print("Parsing stats's --month option")
    elif args.last_month:
        print("Parsing stats's --last-month option")
    elif args._from:
        print("Parsing stats's --from option")
    elif args.to:
        print("Parsing stats's --to option")
    else:
        print("Parsing stats's --today option")


def set_log_parser(subparser):
    log_parser = subparser.add_parser("log", help="Create timelog message")
    log_parser.add_argument("message", help="message that will be logged")
    # call log() function, when processing log command
    log_parser.set_defaults(func=log)


def set_edit_parser(subparser):
    edit_parser = subparser.add_parser("edit", help="Edit timelog file")
    edit_parser.add_argument("-e", "--editor", help="Explicitly set editor")
    # call edit() function, when processing edit command
    edit_parser.set_defaults(func=edit)


def set_stats_parser(subparser):
    stats_parser = subparser.add_parser(
        "stats",
        help="Show how much time was spent working or slacking"
    )

    stats_parser.add_argument("--today",
                              action="store_true",
                              help="Show today's work times (default)")
    stats_parser.add_argument("-y", "--yesterday",
                              action="store_true",
                              help="Show yesterday's work times")
    stats_parser.add_argument("-d", "--day",
                              help="Show specific day's work times")

    stats_parser.add_argument("--week",
                              help="Show specific week's work times")
    stats_parser.add_argument("--last-week",
                              action="store_true",
                              help="Show last week's work times")

    stats_parser.add_argument("--month",
                              help="Show specific month's work times")
    stats_parser.add_argument("--last-month",
                              action="store_true",
                              help="Show last month's work times")

    stats_parser.add_argument("-f", "--from",
                              help="Show work times from specific date",
                              dest="_from")
    stats_parser.add_argument("-t", "--to",
                              help="Show work times from to specific date")

    # call stats() function, when processing stats command
    stats_parser.set_defaults(func=stats)


def parse_args(args):
    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(help="sub-command help")
    set_log_parser(subparser)
    set_edit_parser(subparser)
    set_stats_parser(subparser)

    return parser.parse_args(args)
