import datetime as dt
import re

from collections import defaultdict
from collections import OrderedDict

from timeflow.utils import date_begins
from timeflow.utils import date_ends
from timeflow.utils import get_time
from timeflow.utils import format_duration
from timeflow.utils import LOG_FILE
from timeflow.utils import DATETIME_FORMAT


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


def create_report_as_gtimelog(report_dict):
    output = ""
    project_totals_output = ""
    output += "{}{}\n".format(" " * 64, "time")

    report_dict = OrderedDict(sorted(report_dict.items()))
    total_seconds = 0
    for project in report_dict:
        total_project_seconds = 0
        project_report = report_dict[project]
        for log in project_report:
            entry = "{}: {}".format(project, log)
            seconds = project_report[log]
            time_string = format_duration(seconds)
            output += "{:62s}  {}\n".format(entry, time_string)
            total_project_seconds += seconds
        project_totals_output += "{:62s}  {}\n".format(project, format_duration(total_project_seconds))
        total_seconds += total_project_seconds

    output += "\n"
    output += "Total work done this month: {}\n\n".format(format_duration(total_seconds))
    output += "By category:\n\n"
    output += project_totals_output

    return output


def print_report(work_report_dict, slack_report_dict):
    work_report = create_report(work_report_dict)
    slack_report = create_report(slack_report_dict)
    print('-' * 30, 'WORK', '-' * 31)
    print(work_report)
    print('-' * 30, 'SLACK', '-' * 30)
    print(slack_report)


class Line():
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

    for i, line in enumerate(data[line_begins:line_ends + 1]):
        # if we got to the last line - stop
        if line_begins + i + 1 > line_ends:
            break

        next_line = data[line_begins + i + 1]

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

    for i, line in enumerate(data[line_begins:line_ends + 1]):
        # if we got to the last line - stop
        if line_begins + i + 1 > line_ends:
            break

        next_line = data[line_begins + i + 1]

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
