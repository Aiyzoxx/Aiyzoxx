#!/usr/bin/env python3
"""Render the self-contained static VALTHVN OS profile edition."""
import html
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/desktop'
INK, PAPER, MINT = '#233c35', '#fffdf3', '#c8eedb'
PROJECTS = [('Mint', 'Mint', '01', '#d3edc5'), ('ValthvnQuota', 'ValthvnQuota', '02', '#ffe2ad'),
            ('Antigravity RPC', 'antigravity-discord-rpc', '03', '#d4e5ff')]


def rect(x, y, w, h, fill, stroke=INK, sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def text(x, y, value, size=14, fill=INK, weight=400, family='monospace'):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{html.escape(str(value))}</text>')


def svg(w, h, title, description, body):
    result = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
              f'role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title>'
              f'<desc id="desc">{html.escape(description)}</desc>{body}</svg>\n')
    ET.fromstring(result)
    return result


def window(x, y, w, h, title, fill=PAPER):
    return (rect(x+6, y+6, w, h, INK, INK, 0) + rect(x, y, w, h, fill)
            + rect(x, y, w, 32, MINT) + rect(x+12, y+10, 12, 12, PAPER)
            + text(x+36, y+22, title, 12, weight=700) + text(x+w-24, y+23, '×', 20, weight=700))


def bird(x, y, scale=9):
    pixels = ['       ####       ', '     ##mmmm##     ', '    #mmmmmmmm#    ',
              '   #mmmwwwwmm#    ', '   #mmww#wwwm#    ', '   #mmwwwwwmm#oo  ',
              '  #mmmmwwmmm#oooo ', ' #mmmmmmmmmm#oo   ', '#mmm#mmmmmmm#     ',
              '#mm#mmmmmmmm#     ', ' ##mmmmmmmm#      ', '  #mmmmmmm#       ',
              '   #######        ', '     o o          ', '    oo oo         ']
    colors = {'#': INK, 'm': '#57ad85', 'w': PAPER, 'o': '#e4a348'}
    return ''.join(rect(x+c*scale, y+r*scale, scale, scale, colors[p], 'none', 0)
                   for r, line in enumerate(pixels) for c, p in enumerate(line) if p in colors)


def desktop():
    b = rect(1, 1, 958, 658, '#eaf4dc')
    for x in range(24, 960, 32):
        for y in range(62, 630, 32):
            b += rect(x, y, 2, 2, '#b8cfb8', 'none', 0)
    b += rect(1, 1, 958, 38, INK)
    b += text(22, 26, 'V /', 19, PAPER, 700) + text(83, 25, 'VALTHVN OS', 13, PAPER, 700)
    b += text(270, 25, 'File   Edit   Build   Explore', 12, '#d0e9d9') + text(820, 25, 'EDITION 04', 12, PAPER)
    b += text(36, 109, 'A SMALL DESKTOP.', 13, weight=700)
    b += text(32, 170, 'BIG IDEAS.', 65, weight=900, family='Arial,Helvetica,sans-serif')
    b += text(37, 198, 'Web applications, tools & a little curiosity.', 14)
    b += window(36, 232, 506, 185, 'about_me.txt')
    b += text(58, 301, 'Hey, I’m Valentin.', 29, weight=700, family='Arial,Helvetica,sans-serif')
    b += text(58, 333, 'Vibe coder. Open-source contributor.', 15)
    b += text(58, 360, 'I build web applications, tools and APIs.', 15)
    b += text(58, 391, 'Always learning. Usually building.', 13, '#496456')
    b += window(578, 211, 340, 282, 'bird.app', '#e4f3e7') + bird(659, 266, 10)
    b += text(666, 451, 'SMALL BIRD.', 12, weight=700) + text(654, 474, 'BIG BUILD ENERGY.', 12)
    b += window(36, 444, 506, 165, 'terminal — ~/valthvn', INK)
    b += text(57, 507, '$ cat mindset.txt', 14, '#c5ed99') + text(57, 537, 'make it useful', 16, PAPER)
    b += text(57, 561, 'make it simple', 16, PAPER) + text(57, 585, 'keep shipping_', 16, '#c5ed99')
    b += rect(578, 521, 340, 88, '#ffe2ad') + text(597, 549, '3 PROJECT SHORTCUTS', 12, weight=700)
    b += text(597, 574, 'Pick something below.', 16, weight=700) + text(597, 594, 'Each shortcut opens a repository.', 11)
    b += rect(1, 632, 958, 27, PAPER) + text(18, 651, 'START ↗', 11, weight=700)
    b += text(178, 651, 'about_me.txt   /   bird.app   /   terminal', 11) + text(783, 651, 'built with curiosity', 10)
    return svg(960, 660, 'VALTHVN OS — Valentin’s personal desktop',
               'A mint and cream retro desktop. Valentin: vibe coder and open-source contributor, '
               'building web applications, tools and APIs. An original pixel bird beside a terminal: '
               'make it useful, make it simple, keep shipping. Project links follow below.', b)


def shortcut(label, number, color):
    b = rect(7, 7, 297, 153, INK, INK, 0) + rect(1, 1, 297, 153, PAPER) + rect(1, 1, 297, 27, color)
    b += text(14, 20, 'PROJECT / '+number, 10, weight=700) + text(271, 21, '↗', 16)
    b += '<path d="M20 49 H43 L51 57 H75 V86 H20 Z" fill="'+color+'" stroke="'+INK+'" stroke-width="2"/>'
    b += text(20, 116, label, 21, weight=700, family='Arial,Helvetica,sans-serif') + text(20, 140, 'OPEN REPOSITORY →', 10)
    return svg(306, 162, label+' — open repository', 'Project shortcut linking to '+label+'.', b)


def readme():
    links = '\n'.join(f'<a href="https://github.com/valthvn/{repo}"><img src="./assets/desktop/project-{number}.svg" width="300" alt="Open {label} repository"></a>'
                      for label, repo, number, _ in PROJECTS)
    return '''<!-- VALTHVN OS / V4 — original desktop edition -->

<img src="./assets/desktop/desktop.svg" width="960" alt="VALTHVN OS. Hey, I’m Valentin — vibe coder and open-source contributor building web applications, tools and APIs. Make it useful. Make it simple. Keep shipping.">

<p align="center">
'''+links+'''
</p>

### My toolbox

**Languages** · Python / TypeScript / JavaScript  
**Interfaces** · React / Next.js / Tailwind CSS  
**Behind the scenes** · FastAPI / Node.js / Express  
**Everyday tools** · Docker / Git / Linux / GitHub Actions

<br>

<p align="center">
  <a href="https://github.com/valthvn?tab=repositories">Explore all repositories ↗</a>
  &nbsp; · &nbsp;
  <a href="./docs/versions.md">Change the wallpaper: v1 / v2 / v3 / v4</a>
</p>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'desktop.svg').write_text(desktop(), encoding='utf-8')
    for label, _, number, color in PROJECTS:
        (OUT/f'project-{number}.svg').write_text(shortcut(label, number, color), encoding='utf-8')
    (ROOT/'README.md').write_text(readme(), encoding='utf-8')
    print('Rendered VALTHVN OS / v4: desktop and three linked project shortcuts.')


if __name__ == '__main__':
    main()
