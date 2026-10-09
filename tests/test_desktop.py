"""Validate navigation and GitHub-safe assets for the desktop profile."""
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import render_desktop as desktop


class DesktopTests(unittest.TestCase):
    def test_assets_are_self_contained_accessible_svg(self):
        paths = list((ROOT/'assets/desktop').glob('*.svg'))
        self.assertEqual(len(paths), 4)
        for path in paths:
            root = ET.fromstring(path.read_text(encoding='utf-8'))
            self.assertEqual(root.attrib['role'], 'img')
            for element in root.iter():
                self.assertNotIn(element.tag.split('}')[-1], {'script', 'foreignObject', 'image', 'animate', 'iframe'})
                self.assertFalse(any(key.startswith('on') for key in element.attrib))

    @unittest.skipUnless('VALTHVN OS / V4' in (ROOT/'README.md').read_text(encoding='utf-8'), 'desktop is not active')
    def test_readme_links_assets_and_reproduction(self):
        body = (ROOT/'README.md').read_text(encoding='utf-8')
        self.assertEqual(body, desktop.readme())
        for path in re.findall(r'src="\./([^"]+)"', body):
            self.assertTrue((ROOT/path).is_file(), path)
        for _, repo, _, _ in desktop.PROJECTS:
            self.assertIn(f'href="https://github.com/valthvn/{repo}"', body)
        self.assertEqual((ROOT/'assets/desktop/desktop.svg').read_text(encoding='utf-8'), desktop.desktop())
