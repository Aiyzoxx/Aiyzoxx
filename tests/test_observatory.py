"""Checks for meaningful failure cases: corrupt counts, incomplete calendars,
partial weeks, zero activity and GitHub-compatible self-contained output.
"""
import copy
import datetime as dt
import importlib.util
import json
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def module(name):
    spec=importlib.util.spec_from_file_location(name, ROOT/'scripts'/f'{name}.py')
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


fetch=module('fetch_contributions')
render=module('render_observatory')
TODAY=dt.date(2026,10,9)


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


class ChartTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'data/contributions.json').read_text())
        self.days=render.normalize_days(self.data)
        render.P=render.PALETTES['dark']

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

    def test_candles_use_first_last_min_max_not_invented_prices(self):
        rows=[{'count':x} for x in [3,0,8,2,5,1,4]]
        self.assertEqual(render.candle_summary(rows),dict(open=3,close=4,low=0,high=8,volume=23))
        partial=[{'count':x} for x in [5,2]]
        self.assertEqual(render.candle_summary(partial),dict(open=5,close=2,low=2,high=5,volume=7))

    def test_weekly_totals_preserve_all_observed_days(self):
        groups=render.weekly_groups(self.days)
        flattened=[row for _,rows in groups for row in rows]
        self.assertEqual(flattened,self.days)
        self.assertTrue(all(date.weekday()==0 for date,_ in groups))
        self.assertTrue(all(1<=len(rows)<=7 for _,rows in groups))

    def test_all_zero_activity_renders_valid_svg(self):
        days=[dict(row,count=0) for row in self.days]
        config=json.loads((ROOT/'data/observatory.json').read_text())
        for theme in render.PALETTES.values():
            render.P=theme
            for value in [render.hero(config,days),render.terrain(days),render.signal(days)]:
                ET.fromstring(value)
                self.assertNotRegex(value,r'\b(?:nan|inf)\b')

    def test_generated_svgs_are_self_contained_and_have_static_content(self):
        panels=list((ROOT/'assets').glob('*.svg'))
        self.assertEqual(len(panels),16)
        ns={'s':'http://www.w3.org/2000/svg'}
        for p in panels:
            body=p.read_text()
            root=ET.fromstring(body)
            self.assertIsNotNone(root.find('s:title',ns),p.name)
            self.assertIsNotNone(root.find('s:desc',ns),p.name)
            self.assertFalse(root.findall('.//s:script',ns),p.name)
            self.assertFalse(root.findall('.//s:foreignObject',ns),p.name)
            self.assertNotIn('@import',body)
            self.assertNotIn('opacity="0"',body)
            self.assertNotIn('http://',body.replace('http://www.w3.org/2000/svg',''))
            self.assertNotIn('https://',body)
            self.assertIn('prefers-reduced-motion:reduce',body)

    def test_readme_assets_exist_and_projects_link_to_public_repos(self):
        body=(ROOT/'README.md').read_text()
        for filename in re.findall(r'(?:src|srcset)="\./([^"]+)"',body):
            self.assertTrue((ROOT/filename).is_file(),filename)
        for project in json.loads((ROOT/'data/observatory.json').read_text())['projects']:
            self.assertIn('href="https://github.com/valthvn/'+project['repo']+'"',body)
        self.assertNotIn('mailto:',body)
        self.assertNotIn('VALENT1-streaming',body)
        self.assertNotIn('github-todo-list',body)


if __name__=='__main__':
    unittest.main()
