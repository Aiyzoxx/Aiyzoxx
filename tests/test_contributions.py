"""Validate public calendar parsing and the active profile data window."""
import copy
import datetime as dt
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import fetch_contributions as fetch
import render_session as render
TODAY = dt.date(2026,10,9)


def calendar(overrides=None, skip=None):
    overrides=overrides or {}
    parts=[]
    for i in range(365):
        if i==skip:
            continue
        date=TODAY-dt.timedelta(days=364-i)
        wording=overrides.get(i,'No contributions on this date.')
        parts.append(f'<td class="ContributionCalendar-day" id="day-{i}" data-date="{date}"></td>')
        if wording is not None:
            parts.append(f'<tool-tip for="day-{i}">{wording}</tool-tip>')
    return ''.join(parts)


class CalendarTests(unittest.TestCase):
    def test_counts_and_thousands_separator(self):
        days=fetch.parse_days(calendar({0:'1 contribution on October 10.',364:'1,024 contributions on October 9.'}),TODAY)
        self.assertEqual(len(days),365)
        self.assertEqual(days[0]['count'],1)
        self.assertEqual(days[-1]['count'],1024)
        self.assertEqual(sum(d['count'] for d in days),1025)

    def test_missing_tooltip_fails_instead_of_fabricating_zero(self):
        with self.assertRaisesRegex(ValueError,'Missing or unrecognised'):
            fetch.parse_days(calendar({77:None}),TODAY)

    def test_changed_wording_fails(self):
        with self.assertRaisesRegex(ValueError,'Missing or unrecognised'):
            fetch.parse_days(calendar({77:'A new tooltip format'}),TODAY)

    def test_incomplete_calendar_fails(self):
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            fetch.parse_days(calendar(skip=120),TODAY)

    def test_duplicate_dates_fail(self):
        duplicate=f'<td id="duplicate" data-date="{TODAY}" data-count="0"></td>'
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            fetch.parse_days(calendar()+duplicate,TODAY)

    def test_future_cells_are_not_used(self):
        future=f'<td id="future" data-date="{TODAY+dt.timedelta(days=1)}" data-count="99"></td>'
        days=fetch.parse_days(calendar()+future,TODAY)
        self.assertEqual(days[-1]['date'],TODAY.isoformat())
        self.assertEqual(sum(d['count'] for d in days),0)

    def test_stale_snapshot_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'Stale'):
            fetch.parse_days(calendar(),TODAY+dt.timedelta(days=3))


class ContributionTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT/'data/contributions.json').read_text())
        self.days = render.normalize_days(self.data)

    def test_window_and_counts_match_observed_data(self):
        self.assertEqual(len(self.days),365)
        self.assertEqual((self.days[-1]['date']-self.days[0]['date']).days,364)
        source={d['date']:d['count'] for d in self.data['days']}
        for row in self.days:
            self.assertEqual(row['count'],source[row['date'].isoformat()])

    def test_missing_dates_do_not_become_zero(self):
        bad=copy.deepcopy(self.data)
        del bad['days'][-15]
        with self.assertRaises(KeyError):
            render.normalize_days(bad)

    def test_negative_count_is_rejected(self):
        bad=copy.deepcopy(self.data)
        bad['days'][-1]['count']=-1
        with self.assertRaises(ValueError):
            render.normalize_days(bad)
