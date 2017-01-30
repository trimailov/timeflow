import datetime as dt

from collections import defaultdict
from collections import OrderedDict

from timeflow.utils import DATETIME_FORMAT
from timeflow.utils import calc_time_diff
from timeflow.utils import date_begins
from timeflow.utils import date_ends
from timeflow.utils import format_duration_long
from timeflow.utils import format_duration_short
from timeflow.utils import get_time
from timeflow.utils import parse_lines
from timeflow.utils import strip_log


def get_total_stats_times(work_time, slack_time, today_work_time):
    """
    Returns string output for totals times spent working and slacking
    """
    output = 'Work: {}\n'.format(format_duration_short(sum(work_time)))
    output += 'Slack: {}'.format(format_duration_short(sum(slack_time)))

    if today_work_time:
        today_hours, today_minutes = get_time(today_work_time)
        output += '\n\nToday working for: {}'.format(
            format_duration_short(today_work_time)
        )
    return output


def create_report(report_dict):
    """
    Returns string output for stats report
    """
    output = ""

    report_dict = OrderedDict(sorted(report_dict.items()))
    for project in report_dict:
        project_output = "{}:\n".format(project)
        project_report = report_dict[project]
        total_seconds = 0
        for log in project_report:
            log_seconds = project_report[log]
            total_seconds += log_seconds

            # if log is empty - just state the project name
            if not log:
                log = project

            project_output += "    {time}: {log}\n".format(
                time=format_duration_long(log_seconds),
                log=log
            )
        project_output += "    Total: {time}\n".format(
            time=format_duration_long(total_seconds),
        )
        output += project_output
        output += '\n'

    # remove trailing newlines as they may add up in the pipeline
    return output.strip('\n')


def create_full_report(work_report_dict, slack_report_dict):
    """
    Returns report for both - work and slack
    """
    output = ""
    work_report = create_report(work_report_dict)
    slack_report = create_report(slack_report_dict)
    output += "{:-^67s}\n".format(" WORK ")
    output += work_report
    output += "\n"  # I want empty line between work and slack report
    output += "{:-^67s}\n".format(" SLACK ")
    output += slack_report
    return output


def create_report_as_gtimelog(report_dict):
    """
    Returns string output for report which is generated as in gtimelog
    """
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
            time_string = format_duration_short(seconds)
            output += "{:62s}  {}\n".format(entry, time_string)
            total_project_seconds += seconds
        project_totals_output += "{:62s}  {}\n".format(project, format_duration_short(total_project_seconds))
        total_seconds += total_project_seconds

    output += "\n"
    output += "Total work done this month: {}\n\n".format(format_duration_short(total_seconds))
    output += "By category:\n\n"
    output += project_totals_output

    return output


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
