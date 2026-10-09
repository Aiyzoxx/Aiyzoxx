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

    def test_no_scripts_external_assets_and_reduced_motion(self):
        for name in ('boot.svg','activity.svg'):
            body = (ROOT/'assets/session'/name).read_text(encoding='utf-8')
            ET.fromstring(body)
            self.assertIn('prefers-reduced-motion:reduce',body)
            self.assertIn('animation:none',body)
            self.assertNotIn('<script',body)
            self.assertNotIn('<foreignObject',body)
            self.assertNotIn('href=',body)

    @unittest.skipUnless('SESSION 005' in (ROOT/'README.md').read_text(encoding='utf-8'),'session is not active')
    def test_all_readme_assets_and_clickable_commands(self):
        body = (ROOT/'README.md').read_text(encoding='utf-8')
        for path in re.findall(r'src="\./([^"]+)"',body):
            self.assertTrue((ROOT/path).is_file(),path)
        self.assertEqual(body.count('<details>'),2)
        for _,repo,_,_ in session.PROJECTS:
            self.assertIn('href="https://github.com/valthvn/'+repo+'"',body)
