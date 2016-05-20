import calendar
import datetime as dt
import os
import re
import sys

from collections import defaultdict
from collections import OrderedDict
from pkg_resources import get_distribution


# SETTINGS
__version__ = get_distribution("timeflow").version

LOG_FILE = os.path.expanduser('~') + '/.timeflow'
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DATE_FORMAT = "%Y-%m-%d"
# length of date string
DATE_LEN = 10
# length of datetime string
DATETIME_LEN = 16


def write_to_log_file(message):
    log_message = form_log_message(message)
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
    with open(LOG_FILE, 'a') as fp:
        fp.write(log_message)


def form_log_message(message):
    time_str = dt.datetime.now().strftime(DATETIME_FORMAT)
    log_message = ': '.join((time_str, message))
    if is_another_day():
        log_message = '\n' + log_message
    return log_message + '\n'


def is_another_day():
    """
    Checks if new message is written in the next day,
    than the last log entry.

    date - message date
    """
    try:
        f = open(LOG_FILE, 'r')
        last_line = f.readlines()[-1]
    except (IOError, IndexError):
        return False

    last_log_date = last_line[:DATE_LEN]

    # if message date is other day than last log entry return True, else False
    if dt.datetime.now().strftime(DATE_FORMAT) != last_log_date:
        return True
    else:
        return False


def find_date_line(lines, date_to_find, reverse=False):
    "Returns line index of lines, with date_to_find"
    len_lines = len(lines) - 1
    if reverse:
        lines = reversed(lines)
    for i, line in enumerate(lines):
        date_obj = dt.datetime.strptime(line[:DATE_LEN], DATE_FORMAT)
        date_to_find_obj = dt.datetime.strptime(date_to_find, DATE_FORMAT)

        if reverse and date_obj <= date_to_find_obj:
            return len_lines - i
        elif not reverse and date_obj >= date_to_find_obj:
            return i


def date_begins(lines, date_to_find):
    "Returns first line out of lines, with date_to_find"
    return find_date_line(lines, date_to_find)


def date_ends(lines, date_to_find):
    "Returns last line out of lines, with date_to_find"
    return find_date_line(lines, date_to_find, reverse=True)


def get_time(seconds):
    hours = seconds // 3600
    minutes = seconds % 3600 // 60
    return hours, minutes


def get_this_week():
    now = dt.datetime.now()

    weekday = now.isocalendar()[2] - 1
    this_monday = now - dt.timedelta(days=weekday)
    this_sunday = this_monday + dt.timedelta(days=6)

    date_from = this_monday.strftime(DATE_FORMAT)
    date_to = this_sunday.strftime(DATE_FORMAT)
    return date_from, date_to


def get_last_week():
    week_ago = dt.datetime.now() - dt.timedelta(weeks=1)

    weekday = week_ago.isocalendar()[2] - 1
    last_monday = week_ago - dt.timedelta(days=weekday)
    last_sunday = last_monday + dt.timedelta(days=6)

    date_from = last_monday.strftime(DATE_FORMAT)
    date_to = last_sunday.strftime(DATE_FORMAT)
    return date_from, date_to


def get_week_range(date):
    date = dt.datetime.strptime(date, DATE_FORMAT)

    weekday = date.isocalendar()[2] - 1
    monday = date - dt.timedelta(days=weekday)
    sunday = monday + dt.timedelta(days=6)

    date_from = monday.strftime(DATE_FORMAT)
    date_to = sunday.strftime(DATE_FORMAT)
    return date_from, date_to


def parse_month_arg(arg):
    def is_int(arg):
        try:
            int(arg)
            return True
        except ValueError:
            return False

    if is_int(arg):
        # if it's only integer - it's only month number
        month = int(arg)
        if month < 1 or month > 12:
            sys.exit('Month must be in range from 1 to 12')
        return dt.datetime.now().year, month

    # otherwise argument must be in form 'YYYY-MM'
    year, month = arg.split('-')
    if is_int(year) and is_int(month):
        month = int(month)
        if month < 1 or month > 12:
            sys.exit('Month must be in range from 1 to 12')
        return int(year), month
    else:
        sys.exit('Argument in form of YYYY-MM is expected, e.g. 2015-9')


def get_month_range(arg):
    year, month = parse_month_arg(arg)
    days_in_month = calendar.monthrange(year, month)[1]

    date_from = '{}-{:02}-01'.format(year, month)
    date_to = '{}-{:02}-{:02}'.format(year, month, days_in_month)

    return date_from, date_to


def get_this_month():
    now = dt.datetime.now()

    date_from = now.replace(day=1).strftime(DATE_FORMAT)
    date_to = now.strftime(DATE_FORMAT)

    return date_from, date_to


def get_last_month():
    current_month = dt.datetime.now().replace(day=1)
    last_month = current_month - dt.timedelta(days=1)
    arg = "{}-{}".format(last_month.year, last_month.month)
    return get_month_range(arg)


def print_stats(work_time, slack_time, today_work_time):
    work_hours, work_minutes = get_time(sum(work_time))
    slack_hours, slack_minutes = get_time(sum(slack_time))

    work_string = 'Work: {:02}h {:02}min'.format(work_hours, work_minutes)
    slack_string = 'Slack: {:02}h {:02}min'.format(slack_hours, slack_minutes)

    print(work_string)
    print(slack_string)

    if today_work_time:
        today_hours, today_minutes = get_time(today_work_time)
        work_string = '\nToday working for: {:02}h {:02}min'.format(
            today_hours, today_minutes
        )
        print(work_string)


def create_report(report_dict):
    reports = []
    report_dict = OrderedDict(sorted(report_dict.items()))
    for project in report_dict:
        report = "{}:\n".format(project)
        project_report = report_dict[project]
        total_seconds = 0
        for log in project_report:
            total_seconds += project_report[log]
            hr, mn = get_time(project_report[log])

            # do not leave trailing space if there is no log
            if log:
                report += "    {hours}h {minutes:02}min: {log}\n".format(
                    hours=hr,
                    minutes=mn,
                    log=log
                )
            else:
                report += "    {hours}h {minutes:02}min\n".format(
                    hours=hr,
                    minutes=mn
                )

        hr, mn = get_time(total_seconds)
        report += "    Total: {hours}h {minutes:02}min\n".format(
            hours=hr,
            minutes=mn
        )
        reports.append(report)
    return '\n'.join(reports)


def print_report(work_report_dict, slack_report_dict):
    work_report = create_report(work_report_dict)
    slack_report = create_report(slack_report_dict)
    print('-' * 30, 'WORK', '-' * 31)
    print(work_report)
    print('-' * 30, 'SLACK', '-' * 30)
    print(slack_report)


class Line():
    __slots__ = ['date', 'time', 'project', 'log', 'is_slack']

    def __init__(self, date, time, project, log, is_slack):
        self.date = date
        self.time = time
        self.project = project
        self.log = log
        self.is_slack = is_slack


def clean_line(time, project, log):
    "Cleans line data from unnecessary chars"
    # time has extra colon at the end, so we remove it
    time = time[:-1]

    # project and log can have new line char at the end, remove it
    if project and project[-1] == '\n':
        project = project[:-1]

    if log and log[-1] == '\n':
        log = log[:-1]

    return time, project, log


def parse_message(message):
    "Parses message as log can be empty"
    parsed_message = re.split(r': ', message, maxsplit=1)

    # if parsed message has only project stated, then log is empty
    if len(parsed_message) == 1:
        if type(parsed_message) == list:
            project = parsed_message[0]
        else:
            project = parsed_message
        log = ''
    else:
        project, log = parsed_message

    return project, log


def find_slack(project, log):
    if project.endswith("**") or log.endswith("**"):
        return True
    return False


def strip_log(string):
    "Strips string from slack marks and leading/trailing spaces"
    if string.endswith("**"):
        string = string[:-2]
    return string.strip()


def parse_line(line):
    """Parses log line into logical units: time, project and message

    Log line looks like this:
    [date]_[time]:_[project]:_[log message]
    """
    # get date time and the rest of a message
    date, time, message = re.split(r' ', line, maxsplit=2)

    project, log = parse_message(message)
    time, project, log = clean_line(time, project, log)
    is_slack = find_slack(project, log)

    return Line(date, time, project, log, is_slack)


def parse_lines():
    """Returns a list of objects representing log file"""
    lines = read_log_file_lines()
    data = []
    for line in lines:
        data.append(parse_line(line))
    return data


def calc_time_diff(line, next_line):
    line_time = dt.datetime.strptime(
        "{} {}".format(line.date, line.time),
        DATETIME_FORMAT
    )
    next_line_time = dt.datetime.strptime(
        "{} {}".format(next_line.date, next_line.time),
        DATETIME_FORMAT
    )
    return (next_line_time - line_time).seconds


def calculate_stats(lines, date_from, date_to, today=False):
    work_time = []
    slack_time = []

    line_begins = date_begins(lines, date_from)
    line_ends = date_ends(lines, date_to)

    date_not_found = (line_begins is None or line_ends < line_begins)
    if date_not_found:
        return work_time, slack_time

    data = parse_lines()

    for i, line in enumerate(data[line_begins:line_ends+1]):
        # if we got to the last line - stop
        if line_begins+i+1 > line_ends:
            break

        next_line = data[line_begins+i+1]

        line_date = line.date
        next_line_date = next_line.date

        # if it's day switch, skip this cycle
        if line_date != next_line_date:
            continue

        if next_line.is_slack:
            slack_time.append(calc_time_diff(line, next_line))
        else:
            work_time.append(calc_time_diff(line, next_line))

    today_work_time = None
    if today:
        today_start_time = dt.datetime.strptime(
            "{} {}".format(data[line_begins].date, data[line_begins].time),
            DATETIME_FORMAT
        )
        today_work_time = (dt.datetime.now() - today_start_time).seconds

    return work_time, slack_time, today_work_time


def calculate_report(lines, date_from, date_to):
    """Creates and returns report dictionaries

    Report dicts have form like this:
    {<Project>: {<log_message>: <accumulative time>},
                {<log_message1>: <accumulative time1>}}
    """
    work_dict = defaultdict(lambda: defaultdict(dict))
    slack_dict = defaultdict(lambda: defaultdict(dict))

    line_begins = date_begins(lines, date_from)
    line_ends = date_ends(lines, date_to)

    date_not_found = (line_begins is None or line_ends < line_begins)
    if date_not_found:
        return work_dict, slack_dict

    data = parse_lines()

    for i, line in enumerate(data[line_begins:line_ends+1]):
        # if we got to the last line - stop
        if line_begins+i+1 > line_ends:
            break

        next_line = data[line_begins+i+1]

        line_date = line.date
        next_line_date = next_line.date
        # if it's day switch, skip this cycle
        if line_date != next_line_date:
            continue

        time_diff = calc_time_diff(line, next_line)

        project = strip_log(next_line.project)
        log = strip_log(next_line.log)
        if next_line.is_slack:
            # if log message is identical add time_diff
            # to total time of the log
            if slack_dict[project][log]:
                total_time = slack_dict[project][log]
                total_time += time_diff
                slack_dict[project][log] = total_time
            else:
                slack_dict[project][log] = time_diff
        else:
            if work_dict[project][log]:
                total_time = work_dict[project][log]
                total_time += time_diff
                work_dict[project][log] = total_time
            else:
                work_dict[project][log] = time_diff

    return work_dict, slack_dict


def read_log_file_lines():
    with open(LOG_FILE, 'r') as fp:
        return [line for line in fp.readlines() if line != '\n']
