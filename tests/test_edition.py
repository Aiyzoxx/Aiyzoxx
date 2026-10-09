"""Validate real embedded captures and the editorial profile's actual data."""
import base64
import hashlib
import importlib.util
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import render_edition as render

NS={'s':'http://www.w3.org/2000/svg'}


class EditionTests(unittest.TestCase):
    def test_screenshot_sources_retain_original_git_blob_bytes(self):
        meta=json.loads((ROOT/'assets/edition/source/sources.json').read_text())
        for source in meta:
            data=(ROOT/'assets/edition/source'/source['file']).read_bytes()
            actual=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
            self.assertEqual(actual,source['git_blob_sha'],source['file'])
            self.assertEqual(len(data),source['bytes'])

    def test_embedded_screenshots_are_the_exact_source_pngs(self):
        expected={p.read_bytes() for p in (ROOT/'assets/edition/source').glob('*.png')}
        seen=set()
        for p in (ROOT/'assets/edition').glob('*.svg'):
            root=ET.fromstring(p.read_text())
            for image in root.findall('.//s:image',NS):
                href=image.get('href')
                self.assertTrue(href.startswith('data:image/png;base64,'))
                decoded=base64.b64decode(href.split(',',1)[1],validate=True)
                self.assertIn(decoded,expected,p.name)
                seen.add(decoded)
        self.assertEqual(seen,expected)

    def test_article_links_and_panel_assets_are_valid(self):
        body=(ROOT/'README.md').read_text()
        if 'ÉDITION / V2' not in body:
            self.skipTest('The active README displays another saved edition')
        for filename in re.findall(r'src="\./([^"]+)"',body):
            self.assertTrue((ROOT/filename).is_file(),filename)
        config=json.loads((ROOT/'data/edition.json').read_text())
        for project in config['projects']:
            self.assertIn('href="https://github.com/valthvn/'+project['repo']+'"',body)
        self.assertNotIn('mailto:',body)

    def test_field_notes_use_exactly_the_last_90_real_counts(self):
        data=json.loads((ROOT/'data/contributions.json').read_text())
        days=render.normalize_days(data)
        recent,d,points=render.activity_geometry(days)
        self.assertEqual(recent,days[-90:])
        self.assertEqual(len(points),90)
        self.assertEqual(points[0][0],38)
        self.assertEqual(points[-1][0],882)
        config=json.loads((ROOT/'data/edition.json').read_text())
        output=render.colophon(config,data,days)
        self.assertIn(f'{sum(row["count"] for row in recent)} CONTRIBUTIONS',output)
        self.assertIn(days[-1]['date'].strftime('%d %b %Y').upper(),output)
        self.assertEqual(d.count(' L '),89)
        zeros=[dict(row,count=0) for row in days]
        _,_,flat=render.activity_geometry(zeros)
        self.assertTrue(all(y==183 for _,y in flat))

    def test_panels_are_static_accessible_and_self_contained(self):
        panels=list((ROOT/'assets/edition').glob('*.svg'))
        self.assertEqual(len(panels),5)
        for p in panels:
            body=p.read_text()
            root=ET.fromstring(body)
            self.assertIsNotNone(root.find('s:title',NS),p.name)
            self.assertIsNotNone(root.find('s:desc',NS),p.name)
            self.assertEqual(root.get('viewBox').split()[:3],['0','0','920'])
            self.assertFalse(root.findall('.//s:script',NS),p.name)
            self.assertFalse(root.findall('.//s:foreignObject',NS),p.name)
            self.assertNotIn('https://',body,p.name)
            self.assertNotIn('@import',body,p.name)
            self.assertNotIn('opacity="0"',body,p.name)
            self.assertIn('prefers-reduced-motion:reduce',body,p.name)
            self.assertNotRegex(body,r'\b(?:nan|inf)\b')


if __name__=='__main__':
    unittest.main()
