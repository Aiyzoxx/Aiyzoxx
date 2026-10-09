"""Check real-day semantics, safe motion and the actual README navigation."""
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import render_session as session


class SessionTests(unittest.TestCase):
    def test_portrait_alignment_does_not_depend_on_whitespace(self):
        ns = {'s':'http://www.w3.org/2000/svg'}
        root = ET.fromstring(session.hero())
        group = root.find('.//s:g[@transform="translate(558 212)"]',ns)
        rows = ET.parse(ROOT/'ascii-portrait.svg').getroot().findall('.//s:text',ns)[1:-1]
        visible = [(i,n.text) for i,n in enumerate(rows) if (n.text or '').strip()]
        output = group.findall('.//s:text',ns)
        self.assertEqual(len(output),len(visible))
        for node,(row,source) in zip(output,visible):
            characters = [(column,char) for column,char in enumerate(source) if char != ' ']
            self.assertEqual(node.text,''.join(char for _,char in characters))
            self.assertEqual([float(x) for x in node.attrib['x'].split()],
                             [round(column*3.72,2) for column,_ in characters])
            self.assertAlmostEqual(float(node.attrib['y']),8+row*6.2)

    def test_portrait_prints_rows_in_sequence_with_a_moving_cursor(self):
        ns = {'s':'http://www.w3.org/2000/svg'}
        root = ET.fromstring(session.hero())
        clips = root.findall('.//s:rect[@class="portrait-clip"]',ns)
        cursors = root.findall('.//s:rect[@class="portrait-cursor"]',ns)
        self.assertEqual(len(clips),53)
        self.assertEqual(len(cursors),53)
        timing = [dict(p.split(':',1) for p in node.attrib['style'].split(';')) for node in clips]
        starts = [float(t['--row-delay'][:-1]) for t in timing]
        duration = float(timing[0]['--row-duration'][:-1])
        self.assertAlmostEqual(starts[0],2.6)
        self.assertAlmostEqual(starts[-1]+duration,8.4,places=5)
        for left,right in zip(starts,starts[1:]):
            self.assertAlmostEqual(right-left,duration,places=5)
        self.assertIn('.portrait-cursor{display:none}',session.hero())

    def test_activity_preserves_each_observed_count_including_zero(self):
        data = json.loads((ROOT/'data/contributions.json').read_text())
        for zeros in (False,True):
            if zeros:
                data['days'] = [dict(day,count=0) for day in data['days']]
            root = ET.fromstring(session.activity(data))
            bars = [e for e in root.iter() if 'data-date' in e.attrib]
            self.assertEqual(len(bars),90)
            expected = session.normalize_days(data)[-90:]
            self.assertEqual([(e.attrib['data-date'],int(e.attrib['data-count'])) for e in bars],
                             [(str(d['date']),d['count']) for d in expected])

    def test_candles_use_previous_and_current_seven_day_totals(self):
        data = json.loads((ROOT/'data/contributions.json').read_text())
        days = session.normalize_days(data)
        for i,day in enumerate(days):
            day['count'] = i%11
        for i,candle in enumerate(session.candles(days),start=275):
            opening = sum(day['count'] for day in days[i-7:i])
            closing = sum(day['count'] for day in days[i-6:i+1])
            self.assertEqual((candle['open'],candle['close']),(opening,closing))
            self.assertEqual((candle['low'],candle['high']),(min(opening,closing),max(opening,closing)))
        for day in days:
            day['count'] = 0
        for candle in session.candles(days):
            self.assertEqual((candle['open'],candle['close'],candle['count']),(0,0,0))

    def test_no_scripts_external_assets_and_reduced_motion(self):
        for name in ('boot.svg','activity.svg'):
            body = (ROOT/'assets/session'/name).read_text(encoding='utf-8')
            ET.fromstring(body)
            self.assertIn('prefers-reduced-motion:reduce',body)
            self.assertIn('animation:none',body)
            self.assertNotIn('<script',body)
            self.assertNotIn('<foreignObject',body)
            self.assertNotIn('href=',body)

    def test_all_readme_assets_and_clickable_commands(self):
        body = (ROOT/'README.md').read_text(encoding='utf-8')
        for path in re.findall(r'(?:src|srcset)="\./([^"]+)"',body):
            self.assertTrue((ROOT/path).is_file(),path)
        self.assertEqual(body.count('<details>'),2)
        for removed in ('`history`','`ls -a`','`man session`'):
            self.assertNotIn(removed,body)
        for _,repo,_ in session.PROJECTS:
            self.assertIn('href="https://github.com/valthvn/'+repo+'"',body)

    def test_panels_have_transparent_background_and_light_theme_variants(self):
        ns = {'s':'http://www.w3.org/2000/svg'}
        for name in ('boot','activity','project-01','project-02','project-03'):
            for suffix in ('','-light'):
                body = (ROOT/f'assets/session/{name}{suffix}.svg').read_text(encoding='utf-8')
                root = ET.fromstring(body)
                for rect in root.findall('s:rect',ns):
                    self.assertFalse(rect.get('x')=='0' and rect.get('y')=='0'
                                     and rect.get('width')==root.get('width') and rect.get('height')==root.get('height'))
                if suffix:
                    self.assertIn('#1f2328',body)
                    self.assertNotIn('#f0f0f0',body)
        body = session.readme()
        self.assertEqual(body.count('prefers-color-scheme: dark'),5)
        self.assertEqual(body.count('<picture>'),5)
