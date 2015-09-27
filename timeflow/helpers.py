from collections import OrderedDict
from datetime import datetime as dt
from datetime import timedelta
import os


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


def read_log_file_lines():
    with open(LOG_FILE, 'r') as fp:
        return [line for line in fp.readlines() if line != '\n']


def form_log_message(message):
    time_str = dt.now().strftime(DATETIME_FORMAT)
    log_message = ': '.join((time_str, message))
    if is_another_day():
        return '\n' + log_message + '\n'
    else:
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
    if dt.now().strftime(DATE_FORMAT) != last_log_date:
        return True
    else:
        return False


def find_date_line(lines, date_to_find, reverse=False):
    "Returns line index of lines, with date_to_find"
    len_lines = len(lines) - 1
    if reverse:
        lines = reversed(lines)
    for i, line in enumerate(lines):
        date_obj = dt.strptime(line[:DATE_LEN], DATE_FORMAT)
        date_to_find_obj = dt.strptime(date_to_find, DATE_FORMAT)

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


def get_last_week():
    week_ago = dt.now() - timedelta(weeks=1)
    last_monday = week_ago - timedelta(days=week_ago.isocalendar()[2]-1)
    last_sunday = last_monday + timedelta(days=6)

    date_from = last_monday.strftime(DATE_FORMAT)
    date_to = last_sunday.strftime(DATE_FORMAT)
    return date_from, date_to


def get_month(month, year=dt.now().year):
    month = int(month)
    days_in_month = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }
    date_from = '{}-{:02}-01'.format(year, month)
    date_to = '{}-{:02}-{:02}'.format(year, month, days_in_month[month])
    return date_from, date_to


def get_last_month():
    month = dt.now().month - 1
    if month == 12:
        return get_month(month, year=dt.now().year-1)
    return get_month(month)


def print_stats(work_time, slack_time):
    work_hours, work_minutes = get_time(sum(work_time))
    slack_hours, slack_minutes = get_time(sum(slack_time))

    work_string = 'Work: {:02}h {:02}min'.format(work_hours, work_minutes)
    slack_string = 'Slack: {:02}h {:02}min'.format(slack_hours, slack_minutes)

    print(work_string)
    print(slack_string)


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
        report += "Total: {hours}h {minutes:02}min\n".format(
            hours=hr,
            minutes=mn
        )
        reports.append(report)
    return '\n'.join(reports)


def print_report(work_report_dict, slack_report_dict):
    work_report = create_report(work_report_dict)
    slack_report = create_report(slack_report_dict)
    print(work_report)
    print('-' * 80)
    print(slack_report)
