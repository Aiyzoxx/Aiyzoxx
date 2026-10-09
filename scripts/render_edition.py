#!/usr/bin/env python3
"""Édition: an editorial SVG profile with locally embedded, unaltered UI captures.

Uses only Python's standard library. The bird halftone is derived from the
existing ASCII vector artwork, not a new photo. All project links live in HTML.
"""
from __future__ import annotations

import base64
import datetime as dt
import html
import json
import math
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

from render_observatory import normalize_days

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'assets/edition'
W = 920
C = dict(paper='#f4f1e9', ink='#202422', muted='#60655f', faint='#797e77',
         blue='#234ad8', rule='#cfcec4', wash='#e9e6dc', bluewash='#e2e7f7',
         dark='#222723', white='#f5f5ee')


def esc(value):
    return html.escape(str(value),quote=True)


def text(x,y,value,size=12,color='ink',family='sans',weight=400,anchor='start',spacing=None,extra=''):
    fonts={'sans':'Arial, Helvetica, sans-serif','serif':'Georgia, Times New Roman, serif',
           'mono':'ui-monospace, SFMono-Regular, Consolas, monospace'}
    tracking=f' letter-spacing="{spacing}"' if spacing is not None else ''
    return (f'<text x="{x}" y="{y}" font-family="{fonts[family]}" font-size="{size}" '
            f'font-weight="{weight}" fill="{C[color]}" text-anchor="{anchor}"{tracking} {extra}>{esc(value)}</text>')


def line(x1,y1,x2,y2,color='rule',width=1,extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C[color]}" stroke-width="{width}" {extra}/>'


def path(d,color='blue',width=1,fill='none',extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{C[color]}" stroke-width="{width}" {extra}/>'


def rect(x,y,w,h,color='wash',extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{C[color]}" {extra}/>'


def dot(x,y,r=2,color='blue',extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C[color]}" {extra}/>'


def panel(body,height,title,description):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
            f'role="img" aria-labelledby="title description"><title id="title">{esc(title)}</title>'
            f'<desc id="description">{esc(description)}</desc>'
            '<style>'
            '@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}'
            '@keyframes breathe{0%,100%{opacity:.45}50%{opacity:1}}'
            '.draw{stroke-dasharray:1;animation:draw 1.8s ease-out both}'
            '.pulse{animation:breathe 4s ease-in-out infinite}'
            '@media(prefers-reduced-motion:reduce){.draw,.pulse{animation:none}}'
            '</style>'+rect(0,0,W,height,'paper')+''.join(body)+'</svg>\n')


def arrow(x,y):
    return path(f'M {x} {y+15} L {x+15} {y} M {x} {y} H {x+15} V {y+15}','blue',1.5)


def embedded_image(name,x,y,w):
    content=(DEST/'source'/name).read_bytes()
    if content[:8]!=b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'Expected PNG screenshot: {name}')
    width,height=struct.unpack('>II',content[16:24])
    h=w*height/width
    encoded=base64.b64encode(content).decode('ascii')
    return (f'<image x="{x}" y="{y}" width="{w}" height="{h:.2f}" '
            f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{encoded}"/>',h)


def bird_vector(x,y,width=266):
    """Convert the old SVG's density ramp to native dots, retaining its subject."""
    root=ET.fromstring((ROOT/'ascii-portrait.svg').read_text())
    rows=[t.text or '' for t in root.iter('{http://www.w3.org/2000/svg}text') if 'textLength' in t.attrib]
    if len(rows)!=53 or any(len(r)!=100 for r in rows):
        raise ValueError('Expected the original 100 × 53 ASCII portrait grid')
    ramp=" .`:-=+*cs#%@"
    step=width/50
    b=['<g aria-label="Bird avatar, halftone study from existing vector artwork">']
    for ry,row in enumerate(rows):
        for rx in range(0,100,2):
            char=row[rx]
            density=ramp.index(char)/(len(ramp)-1)
            if density:
                r=.40+2.0*math.sqrt(density)
                b.append(dot(round(x+rx/2*step,2),round(y+ry*step,2),round(r,2),'ink'))
    b.append('</g>')
    return ''.join(b)


def cover(config):
    b=[text(36,34,'ÉDITION',20,family='serif'),text(156,34,'A PERSONAL SOFTWARE JOURNAL',10,'muted',family='mono',spacing=.7),
       text(884,34,'VOL. 02 / 2026',10,'blue',family='mono',anchor='end'),
       line(36,52,884,52,'ink',1.2),text(27,177,config['username'],145,weight=700,spacing=-10),
       text(36,278,config['headline'],49,family='serif',spacing=-1.8),
       path('M 38 292 C 163 279 300 300 469 284','blue',2.4,extra='class="draw" pathLength="1"'),
       text(38,346,config['intro'][0],15,'muted'),text(38,370,config['intro'][1],15,'muted'),
       text(38,422,' / '.join(config['stack']),11,'ink',family='mono'),
       text(38,475,'SELECTED WORK',10,'blue',family='mono',spacing=1),
       text(38,496,'01 Mint     02 ValthvnQuota     03 Antigravity RPC',11,'muted',family='mono'),
       bird_vector(599,190,270),
       text(600,495,'FIG. 01 / BIRD STUDY, IN DOTS',9,'muted',family='mono'),
       line(36,529,884,529,'ink',1.2),
       text(36,553,'USEFUL SOFTWARE / CONSIDERED DETAILS',9,'muted',family='mono',spacing=.5),
       text(884,553,'VALTHVN — EDITION TWO',9,'muted',family='mono',anchor='end')]
    return panel(b,574,'valthvn — Édition, a personal software journal',
                 'Volume two. Ideas, made useful. C#, Python, TypeScript and JavaScript. A halftone bird avatar is derived from the existing vector portrait. Three selected public projects follow.')


def mint():
    dashboard,dh=embedded_image('mint-dashboard.png',494,84,204)
    settings,sh=embedded_image('mint-settings.png',699,166,170)
    b=[text(36,33,'01',11,'blue',family='mono'),text(82,33,'DESKTOP / WINDOWS',10,'muted',family='mono',spacing=.6),
       text(854,33,'VIEW PROJECT',10,'blue',family='mono',anchor='end'),arrow(868,20),line(36,52,884,52),
       text(36,139,'Mint',77,family='serif',spacing=-3),
       text(38,190,'A quieter computer.',21,family='serif'),text(38,219,'A clearer picture.',21,family='serif'),
       text(38,270,'Temperature in the system tray.',14,'muted'),
       text(38,294,'A cooling switch, one click away.',14,'muted'),
       text(38,318,'Power settings you can restore.',14,'muted'),
       rect(475,71,409,391,'bluewash'),dashboard,settings,
       path('M 604 249 H 447 V 224','blue',1,extra='class="draw" pathLength="1"'),dot(604,249,2.5),
       text(419,207,'THERMAL',8,'blue',family='mono',anchor='middle'),text(419,219,'READOUT',8,'blue',family='mono',anchor='middle'),
       text(494,457,'A / DASHBOARD',9,'muted',family='mono'),text(699,477,'B / SETTINGS',9,'muted',family='mono'),
       text(38,411,'WINDOWS / .NET',11,family='mono'),
       text(38,438,'Built on Universal x86 Tuning Utility.',10,'muted'),
       line(36,497,884,497),text(36,519,'FIG. 02 / REAL APPLICATION CAPTURES',9,'muted',family='mono'),
       text(884,519,'01 — MINT',9,'blue',family='mono',anchor='end')]
    return panel(b,540,'Mint — a Windows temperature and power utility',
                 'Actual unaltered screenshots: Mint dashboard and settings. CPU temperature, cooling toggle and restorable power settings. Built on Universal x86 Tuning Utility; project license and credits apply.')


def quota():
    flyout,h=embedded_image('quota-flyout.png',60,152,339)
    taskbar,th=embedded_image('quota-taskbar.png',54,76,376)
    b=[text(36,33,'02',11,'blue',family='mono'),text(82,33,'DEVELOPER TOOL / WINDOWS',10,'muted',family='mono',spacing=.6),
       text(854,33,'VIEW PROJECT',10,'blue',family='mono',anchor='end'),arrow(868,20),line(36,52,884,52),
       rect(36,68,397,449,'wash'),taskbar,flyout,
       text(477,149,'Valthvn',62,family='serif',spacing=-2),text(477,216,'Quota',62,family='serif',spacing=-2),
       text(480,264,'Your AI tools, at a glance.',21,family='serif'),
       text(480,310,'Codex and Antigravity usage,',14,'muted'),
       text(480,334,'where you already look: the taskbar.',14,'muted'),
       text(480,382,'WINDOWS / WINUI 3',11,family='mono'),
       text(480,410,'Fork of CodexQuota,',11,'muted'),
       text(480,429,'extended with Antigravity support.',11,'muted'),
       path('M 342 309 H 443 V 361','blue',1,extra='class="draw" pathLength="1"'),dot(342,309,2.5),
       text(451,357,'DAILY USAGE',8,'blue',family='mono'),
       text(60,507,'A / TASKBAR     B / QUOTA FLYOUT',9,'muted',family='mono'),
       line(36,540,884,540),text(36,562,'FIG. 03 / REAL APPLICATION CAPTURES',9,'muted',family='mono'),
       text(884,562,'02 — VALTHVNQUOTA',9,'blue',family='mono',anchor='end')]
    return panel(b,583,'ValthvnQuota — Codex and Antigravity quota monitoring',
                 'Unaltered screenshots of the Windows taskbar widget and Antigravity quota flyout, taken from the public project repository. Screenshot numbers are captured examples, not the current profile owner quota. Fork of CodexQuota, extended with Antigravity support.')


def rpc():
    b=[text(36,33,'03',11,'blue',family='mono'),text(82,33,'WORKFLOW AUTOMATION / PYTHON',10,'muted',family='mono',spacing=.6),
       text(854,33,'VIEW PROJECT',10,'blue',family='mono',anchor='end'),arrow(868,20),line(36,52,884,52),
       text(36,124,'Antigravity',58,family='serif',spacing=-2),text(36,183,'RPC',58,family='serif',spacing=-2),
       text(38,230,'A little more presence.',21,family='serif'),
       text(38,275,'Project, tool and model activity,',14,'muted'),
       text(38,299,'automatically shared through Discord.',14,'muted'),
       text(38,354,'PYTHON / PROCESS WATCHER / DISCORD',10,family='mono'),
       rect(482,84,400,294,'bluewash'),
       text(502,111,'EDITOR',9,'blue',family='mono',spacing=1),
       text(502,142,'Antigravity.exe',18,family='mono'),
       line(501,160,861,160,'rule'),
       text(502,190,'WORKSPACE + TOOL + MODEL',9,'muted',family='mono'),
       path('M 532 206 V 229 H 837','blue',1.5,extra='class="draw" pathLength="1"'),
       dot(532,229,3,'blue',extra='class="pulse"'),
       text(570,220,'watch / translate / update',11,'blue',family='mono'),
       text(502,268,'DISCORD RICH PRESENCE',9,'blue',family='mono',spacing=1),
       text(502,300,'Project: Mint',19,weight=600),
       text(502,327,'Editing code',13,'muted'),
       text(502,356,'Illustrative status / not a live session',9,'muted'),
       line(36,407,884,407),text(36,430,'FIG. 04 / WORKFLOW SCHEMATIC',9,'muted',family='mono'),
       text(884,430,'03 — ANTIGRAVITY RPC',9,'blue',family='mono',anchor='end')]
    return panel(b,451,'Antigravity RPC — editor activity to Discord Rich Presence',
                 'A workflow schematic, not a screenshot or live feed: Antigravity process activity is watched, translated and sent to Discord Rich Presence. The example status Project: Mint / Editing code is illustrative.')


def activity_geometry(days,x=38,y=183,width=844,height=55):
    recent=days[-90:]
    peak=max(d['count'] for d in recent) or 1
    points=[(x+i*width/89,y-height*math.log1p(row['count'])/math.log1p(peak)) for i,row in enumerate(recent)]
    d='M '+' L '.join(f'{px:.2f} {py:.2f}' for px,py in points)
    return recent,d,points


def colophon(config,data,days):
    recent,d,points=activity_geometry(days)
    total=sum(row['count'] for row in recent)
    end=days[-1]['date'].strftime('%d %b %Y').upper()
    b=[text(36,33,'FIELD NOTES',10,'blue',family='mono',spacing=1),
       text(884,33,'90 DAYS / OBSERVED ACTIVITY',10,'muted',family='mono',anchor='end'),
       line(36,52,884,52,'ink',1.2),
       text(36,102,'Work leaves a trace.',34,family='serif'),
       text(884,97,f'{total} CONTRIBUTIONS',11,'blue',family='mono',anchor='end'),
       line(38,183,882,183),path(d,'blue',1.5,extra='class="draw" pathLength="1"'),
       dot(round(points[-1][0],2),round(points[-1][1],2),2.8),
       text(38,207,recent[0]['date'].strftime('%d %b').upper(),9,'muted',family='mono'),
       text(882,207,end,9,'muted',family='mono',anchor='end'),
       line(36,231,884,231,'ink',1.2),
       text(36,263,'COLOPHON',10,'blue',family='mono',spacing=1),
       text(36,293,'Applications. Tools. Experiments.',17,family='serif'),
       text(36,318,' / '.join(config['stack']),11,'muted',family='mono'),
       text(884,263,'EDITION 02 / ARCHIVED AS V2',9,'blue',family='mono',anchor='end'),
       text(884,293,'Real public contributions / daily refresh',10,'muted',anchor='end'),
       text(884,317,'DATA AS OF '+end,9,'muted',family='mono',anchor='end'),
       line(36,343,884,343),
       text(36,368,'VALTHVN / GITHUB',9,'ink',family='mono'),
       text(884,368,'DESIGNED AS A SOFTWARE JOURNAL',9,'muted',family='mono',anchor='end')]
    return panel(b,391,'Field notes — real GitHub activity and profile colophon',
                 f'{total} public contributions in the last 90 observed days, ending {end}. Each point is one real daily count, shown on a log scale. Snapshot fetched {data["generated_at"]}. This measures activity, not productivity.')


def image_block(name,alt,href=None):
    image=f'<img src="./assets/edition/{name}.svg" width="920" alt="{esc(alt)}">'
    return f'<a href="{esc(href)}">\n{image}\n</a>' if href else image


def main():
    config=json.loads((ROOT/'data/edition.json').read_text())
    data=json.loads((ROOT/'data/contributions.json').read_text())
    days=normalize_days(data)
    DEST.mkdir(parents=True,exist_ok=True)
    panels={'cover':cover(config),'mint':mint(),'quota':quota(),'rpc':rpc(),'colophon':colophon(config,data,days)}
    for name,value in panels.items():
        ET.fromstring(value)
        (DEST/f'{name}.svg').write_text(value,encoding='utf-8')
    blocks=[image_block('cover','valthvn — Édition, volume 02. A personal software journal with a halftone bird avatar.')]
    for name,project in zip(('mint','quota','rpc'),config['projects']):
        blocks.append(image_block(name,project['name']+' — '+project['kind']+'. Open the public project.',
                                  'https://github.com/'+config['username']+'/'+project['repo']))
    blocks.append(image_block('colophon','90 days of real public GitHub contributions. Daily refresh and data date.'))
    blocks.append('<p align="center">\n  <a href="https://github.com/valthvn?tab=repositories">All work</a> · '
                  '<a href="./docs/edition.md">Colophon &amp; sources</a> · '
                  '<a href="./docs/versions.md">Back issues: v1 / v2</a>\n</p>')
    (ROOT/'README.md').write_text('<!-- ÉDITION / V2 — generated by scripts/render_edition.py -->\n\n'+
                                '\n\n'.join(blocks)+'\n',encoding='utf-8')
    print(f'Rendered Édition / v2: {len(panels)} panels, real UI captures, '
          f'{sum(d["count"] for d in days[-90:])} contributions in 90 observed days.')


if __name__=='__main__':
    main()
