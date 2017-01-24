import calendar
import datetime as dt
import os
import sys

# SETTINGS
LOG_FILE = os.path.expanduser('~') + '/.timeflow'
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DATE_FORMAT = "%Y-%m-%d"
# length of date string
DATE_LEN = 10
# length of datetime string
DATETIME_LEN = 16


def write_to_log_file(message):
    """
    Writes message to the `LOG_FILE`

    `message`: String
    """
    log_message = form_log_message(message)
    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))
    with open(LOG_FILE, 'a') as fp:
        fp.write(log_message)


def form_log_message(message):
    """
    Joins current time with the log message

    `message`: String
    """
    time_str = dt.datetime.now().strftime(DATETIME_FORMAT)
    log_message = ': '.join((time_str, message))

    # we want easily seeable separation between the days in the log file
    if is_another_day():
        log_message = '\n' + log_message
    return log_message + '\n'


def is_another_day():
    """
    Checks if new message is written in the next day, than the last log entry.
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
    """
    Returns index of line, which matches `date_to_find`
    """
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


def format_duration_short(seconds):
    """
    Formats seconds into hour and minute string

    Does not return hour or minute substring if the value is zero
    """
    h, m = get_time(seconds)
    if h and m:
        return '%d hour%s %d min' % (h, h != 1 and "s" or "", m)
    elif h:
        return '%d hour%s' % (h, h != 1 and "s" or "")
    else:
        return '%d min' % m


def format_duration_long(seconds):
    """
    Formats seconds into hour and minute string

    Always returns full string, even if hours or minutes may be zero
    """
    h, m = get_time(seconds)
    return '%d hour%s %d min' % (h, h != 1 and "s" or "", m)


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
