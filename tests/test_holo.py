"""Check the deliverable is truly animated, projected, readable and data-safe."""
import hashlib
import json
import math
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import animate_holo_card as animation
import render_holo_profile as profile


class HoloTests(unittest.TestCase):
    def test_primary_animation_has_real_frames_and_a_repeat_loop(self):
        meta=json.loads((ROOT/'assets/holo/animation.json').read_text())
        with Image.open(ROOT/'assets/holo/profile.webp') as image:
            self.assertTrue(image.is_animated)
            self.assertEqual(image.n_frames,96)
            self.assertEqual(image.size,(720,740))
            self.assertEqual(image.info['loop'],0)
            fingerprints=[]
            for index in [0,24,48,72]:
                image.seek(index)
                fingerprints.append(hashlib.sha256(image.convert('RGB').tobytes()).hexdigest())
            self.assertEqual(len(set(fingerprints)),4)
        self.assertEqual(meta['loop_ms'],7680)
        self.assertFalse(meta['live_data_in_animation'])

    def test_gif_fallback_is_animated_with_the_same_loop_length(self):
        with Image.open(ROOT/'assets/holo/profile.gif') as image:
            self.assertEqual(image.n_frames,48)
            self.assertEqual(image.size,(540,555))
            self.assertEqual(image.info['loop'],0)
            duration=0
            for index in range(image.n_frames):
                image.seek(index)
                duration += image.info['duration']
            self.assertEqual(duration,7680)

    @unittest.skipUnless('HOLO EX / V3' in (ROOT/'README.md').read_text(), 'holo is not the active profile')
    def test_reduced_motion_selects_one_static_image_first(self):
        body=(ROOT/'README.md').read_text()
        self.assertLess(body.index('prefers-reduced-motion: reduce'),body.index('type="image/webp"'))
        self.assertIn('srcset="./assets/holo/profile-still.png"',body)
        self.assertIn('src="./assets/holo/profile.gif"',body)
        with Image.open(ROOT/'assets/holo/profile-still.png') as image:
            self.assertEqual(getattr(image,'n_frames',1),1)
            self.assertEqual(image.size,(720,740))

    def test_actual_perspective_varies_and_stays_inside_the_canvas(self):
        quads=[animation.card_quad(phase) for phase in [0,.25,.5,.75]]
        self.assertEqual(len({tuple(q) for q in quads}),4)
        for quad in quads:
            for x,y in quad:
                self.assertTrue(0<x<720)
                self.assertTrue(0<y<740)
            left=math.dist(quad[0],quad[3])
            right=math.dist(quad[1],quad[2])
            self.assertGreater(left,500)
            self.assertGreater(right,500)
        # A yawed perspective face is not just a translated/scaled rectangle.
        self.assertGreater(abs(math.dist(quads[1][0],quads[1][3])-math.dist(quads[1][1],quads[1][2])),20)

    def test_inverse_projection_maps_all_four_card_corners(self):
        source=[(0,0),(440,0),(440,616),(0,616)]
        target=animation.card_quad(.23)
        a,b,c,d,e,f,g,h=animation.inverse_homography(source,target)
        for (u,v),(x,y) in zip(source,target):
            denominator=g*x+h*y+1
            self.assertAlmostEqual((a*x+b*y+c)/denominator,u,places=5)
            self.assertAlmostEqual((d*x+e*y+f)/denominator,v,places=5)

    def test_ledger_uses_real_data_separately_from_fictional_card_stats(self):
        data=json.loads((ROOT/'data/contributions.json').read_text())
        days=profile.normalize_days(data)
        output=profile.ledger(data,days)
        for value in [sum(d['count'] for d in days),sum(d['count'] for d in days[-90:]),sum(d['count']>0 for d in days)]:
            self.assertIn('>'+str(value)+'</text>',output)
        self.assertIn('HP and move values on the artwork are fictional',output)
        ET.fromstring(output)
        zeros=[dict(d,count=0) for d in days]
        ET.fromstring(profile.ledger(data,zeros))

    @unittest.skipUnless('HOLO EX / V3' in (ROOT/'README.md').read_text(), 'holo is not the active profile')
    def test_all_readme_assets_and_project_destinations_are_real(self):
        body=(ROOT/'README.md').read_text()
        self.assertIn('HOLO EX / V3',body)
        for name in re.findall(r'(?:src|srcset)="\./([^"]+)"',body):
            self.assertTrue((ROOT/name).is_file(),name)
        config=json.loads((ROOT/'data/holo.json').read_text())
        for project in config['projects']:
            self.assertIn('href="https://github.com/valthvn/'+project['repo']+'"',body)
        self.assertNotIn('mailto:',body)


if __name__=='__main__':
    unittest.main()
