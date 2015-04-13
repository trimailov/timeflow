import unittest

from timeflow.parser import parse_args


class TestParser(unittest.TestCase):
    def test_log(self):
        args = parse_args(['log'])

    def test_edit(self):
        args = parse_args(['edit'])

    def test_edit_e(self):
        args = parse_args(['edit', '-e', 'vim'])

    def test_edit_editor(self):
        args = parse_args(['edit', '--editor', 'vim'])

    def test_stats(self):
        args = parse_args(['stats'])

    def test_stats_today(self):
        args = parse_args(['stats', '--today'])

    def test_stats_yesterday(self):
        args = parse_args(['stats', '--yesterday'])

    def test_stats_day(self):
        args = parse_args(['stats', '--day', '2015-01-01'])

    def test_stats_week(self):
        args = parse_args(['stats', '--week', '2015-01-01'])

    def test_stats_last_week(self):
        args = parse_args(['stats', '--last-week'])

    def test_stats_month(self):
        args = parse_args(['stats', '--month', '2015-01-01'])

    def test_stats_last_month(self):
        args = parse_args(['stats', '--last-month'])

    def test_stats_from(self):
        args = parse_args(['stats', '--from', '2015-01-01'])

    def test_stats_to(self):
        args = parse_args(['stats', '--to', '2015-01-01'])


if __name__ == "__main__":
    unittest.main()
