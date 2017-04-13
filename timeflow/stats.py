import datetime as dt
import smtplib

from collections import defaultdict
from collections import OrderedDict

from timeflow.settings import Settings
from timeflow.utils import DATE_FORMAT
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


def create_report_as_gtimelog(report_dict, literal_time_range=''):
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
    output += "Total work done{}{}: {}\n\n".format(
        ' ' if literal_time_range else '',  # add space if time range exists
        literal_time_range,
        format_duration_short(total_seconds)
    )
    output += "By category:\n\n"
    output += project_totals_output

    return output


def calculate_stats(lines, date_from, date_to, today=False):
    work_time = []
    slack_time = []
    today_work_time = None

    line_begins = date_begins(lines, date_from)
    line_ends = date_ends(lines, date_to)

    date_not_found = (line_begins is None or line_ends < line_begins)
    if date_not_found:
        return work_time, slack_time, today_work_time

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


def get_daily_report_subject(day, person):
    """
    Returns subject string for daily report email

    `day:datetime.date` - date of the day we are reporting for
    `person:str` - reporting person's name, e.g. 'Jon Doe'
    """
    # it's possible to use strftime('%a'), but it's locale sensitive,
    # and I do not want this
    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    calendar_time = "{weekday}, week {week:02}".format(
        weekday=weekday_names[day.isocalendar()[2]],
        week=day.isocalendar()[1],
    )
    subject = "{day} report for {person} ({calendar_time})".format(
        day=day.strftime(DATE_FORMAT),
        person=person,
        calendar_time=calendar_time
    )
    return subject


def get_weekly_report_subject(week_day, person):
    """
    Returns subject string for weekly report email

    `week_day:datetime.date` - any date for the week we are reporting for
    `person:str` - reporting person's name, e.g. 'Jon Doe'
    """
    calendar_time = "week {:02}".format(week_day.isocalendar()[1])
    subject = "Weekly report for {person} ({calendar_time})".format(
        person=person,
        calendar_time=calendar_time
    )
    return subject


def get_monthly_report_subject(month_day, person):
    """
    Returns subject string for monthly report email

    `month_day:datetime.date` - any date for the month we are reporting for
    `person:str` - reporting person's name, e.g. 'Jon Doe'
    """
    calendar_time = "{year}/{month:02}".format(
        year=month_day.year,
        month=month_day.month
    )
    subject = "Monthly report for {person} ({calendar_time})".format(
        person=person,
        calendar_time=calendar_time
    )
    return subject


def get_custom_range_report_subject(date_from, date_to, person):
    subject = "Custom date range report for {person} ({_from:%Y-%m-%d} - {to:%Y-%m-%d})".format(
        person=person,
        _from=date_from,
        to=date_to,
    )
    return subject


def email_report(date_from, date_to, report, email_time_range=None):
    settings = Settings()
    settings.load()

    sender = settings.email_address
    receivers = [settings.activity_email]

    date_from_time_range = dt.datetime.strptime(date_from, DATE_FORMAT)
    subject = ''
    if email_time_range == 'day':
        subject = get_daily_report_subject(date_from_time_range, settings.name)
    elif email_time_range == 'week':
        subject = get_weekly_report_subject(date_from_time_range, settings.name)
    elif email_time_range == 'month':
        subject = get_monthly_report_subject(date_from_time_range, settings.name)
    else:
        # convert date strings to datetime objects
        _date_from = dt.datetime.strptime(date_from, DATE_FORMAT)
        _date_to = dt.datetime.strptime(date_to, DATE_FORMAT)
        subject = get_custom_range_report_subject(_date_from, _date_to, settings.name)
    full_subject = "[Activity] {}".format(subject)

    message = (
        "From: {}\n"
        "To: {}\n"
        "Subject: {}\n\n"
        "{}"
    ).format(sender, ", ".join(receivers), full_subject, report)

    try:
        conn = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        conn.ehlo()
        conn.starttls()
        conn.login(settings.email_user, settings.email_password)
        conn.sendmail(sender, receivers, message)
        print("Successfully sent email")
    except smtplib.SMTPException:
        print("Error: unable to send email")
