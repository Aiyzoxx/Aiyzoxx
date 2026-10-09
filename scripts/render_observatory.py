#!/usr/bin/env python3
"""Generate a self-contained, dual-theme profile from real daily contributions.

No network, fonts, external images or runtime dependencies. Each panel remains
legible with animations disabled; README links are HTML, not links inside SVG.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W = 920
PALETTES = {
    'dark': dict(bg='#101113', fg='#f0eee9', muted='#a6a6a3', faint='#727576',
                 rule='#303235', plane='#17191c', grid='#3a3d40',
                 top='#dedbd4', front='#858b8d', side='#53595d',
                 accent='#dfb06c', wash='#201e1a'),
    'light': dict(bg='#faf9f6', fg='#202326', muted='#62686a', faint='#757a7b',
                  rule='#deddd8', plane='#eeede8', grid='#cccec9',
                  top='#737c81', front='#b7bebf', side='#90999c',
                  accent='#976020', wash='#f1e9dc'),
}


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, size=12, color='fg', weight=400, anchor='start', mono=False, spacing=None):
    font = 'ui-monospace, SFMono-Regular, Consolas, monospace' if mono else 'Arial, Helvetica, sans-serif'
    tracking = f' letter-spacing="{spacing}"' if spacing is not None else ''
    return (f'<text x="{x}" y="{y}" fill="{P[color]}" font-family="{font}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{tracking}>{esc(value)}</text>')


def line(x1, y1, x2, y2, color='rule', width=1, extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{P[color]}" stroke-width="{width}" {extra}/>'


def path(d, color='fg', width=1, fill='none', extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{P[color]}" stroke-width="{width}" {extra}/>'


def dot(x, y, r=2, color='accent', extra=''):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{P[color]}" {extra}/>'


def svg(body, height, title, description):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
            f'viewBox="0 0 {W} {height}" role="img" aria-labelledby="title description">'
            f'<title id="title">{esc(title)}</title><desc id="description">{esc(description)}</desc>'
            '<style>'
            '@keyframes trace{to{stroke-dashoffset:-160}}'
            '@keyframes orbit{to{transform:rotate(360deg)}}'
            '@keyframes enter{from{opacity:.25}to{opacity:1}}'
            '.trace{animation:trace 18s linear infinite}'
            '.orbit{animation:orbit 24s linear infinite;transform-origin:752px 161px}'
            '.enter{animation:enter 1.5s ease-out both}'
            '@media(prefers-reduced-motion:reduce){.trace,.orbit,.enter{animation:none}.orbit{display:none}}'
            '</style>'
            f'<rect width="{W}" height="{height}" fill="{P["bg"]}"/>'
            + ''.join(body) + '</svg>\n')


def label(y, number, title, right):
    return [text(36, y, number, 11, 'accent', mono=True),
            text(70, y, title, 11, 'muted', mono=True, spacing=1),
            text(884, y, right, 11, 'muted', anchor='end', mono=True)]


def normalize_days(data):
    """A 365-day window ending at the last actual date, not the machine clock."""
    raw = data['days']
    if not raw:
        raise ValueError('Contribution data must contain days')
    lookup = {}
    for row in raw:
        date = dt.date.fromisoformat(row['date'])
        count = row['count']
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise ValueError('Contribution counts must be nonnegative integers')
        if date in lookup:
            raise ValueError('Duplicate contribution dates')
        lookup[date] = count
    end = max(lookup)
    start = end - dt.timedelta(days=364)
    # Missing dates within the observed window are errors, never fake zeroes.
    return [{'date': start + dt.timedelta(days=i), 'count': lookup[start + dt.timedelta(days=i)]}
            for i in range(365)]


def weekly_groups(days):
    """Monday-based weeks, keeping partial first/last weeks explicit."""
    groups = {}
    for row in days:
        monday = row['date'] - dt.timedelta(days=row['date'].weekday())
        groups.setdefault(monday, []).append(row)
    return list(sorted(groups.items()))


def candle_summary(rows):
    counts = [d['count'] for d in rows]
    return dict(open=counts[0], close=counts[-1], low=min(counts), high=max(counts), volume=sum(counts))


def hero(config, days):
    last90 = days[-90:]
    b = [text(36, 34, config['eyebrow'], 11, 'muted', mono=True, spacing=1),
         text(884, 34, 'PERSONAL ENGINEERING LOG', 10, 'muted', anchor='end', mono=True),
         line(36, 50, 884, 50),
         text(32, 155, config['username'], 96, weight=700, spacing=-5),
         text(36, 199, config['headline'], 24, weight=400),
         text(36, 234, config['description'], 15, 'muted'),
         text(36, 257, config['description_second_line'], 15, 'muted'),
         text(36, 302, ' / '.join(config['stack']), 11, 'muted', mono=True)]
    cx, cy, radius = 752, 161, 86
    b += [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{P["rule"]}" stroke-width="1"/>' for r in (50, 84, 110)]
    peak = max(d['count'] for d in last90) or 1
    for i, row in enumerate(last90):
        angle = (i / 90) * math.tau - math.pi / 2
        length = 4 + 27 * math.log1p(row['count']) / math.log1p(peak)
        r = radius + length
        x1, y1 = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        x2, y2 = cx + r * math.cos(angle), cy + r * math.sin(angle)
        color = 'accent' if row['count'] else 'grid'
        b.append(line(round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2), color, 2))
    b += [line(cx-8, cy, cx+8, cy, 'muted'), line(cx, cy-8, cx, cy+8, 'muted'),
          text(cx, cy-15, '90', 25, anchor='middle', mono=True),
          text(cx, cy+31, 'DAYS', 9, 'muted', anchor='middle', mono=True, spacing=2),
          '<g class="orbit">'+dot(cx, cy-110, 3)+'</g>',
          text(cx, 296, 'CONTRIBUTION FINGERPRINT', 9, 'muted', anchor='middle', mono=True, spacing=.6),
          text(cx, 314, 'One mark / one day', 10, 'muted', anchor='middle')]
    return svg(b, 338, f'{config["username"]} — software, tools and experiments',
               'A 90-day radial contribution fingerprint: mark length represents the daily count. '+config['headline'])


def polygon(points, fill, stroke='grid', opacity=1):
    pts = ' '.join(f'{x:.2f},{y:.2f}' for x, y in points)
    return f'<polygon points="{pts}" fill="{P[fill]}" stroke="{P[stroke]}" stroke-width=".65" opacity="{opacity}"/>'


def terrain(days):
    total = sum(d['count'] for d in days)
    active = sum(d['count'] > 0 for d in days)
    b = label(31, '01', 'ACTIVITY TERRAIN', '365 DAYS / DAILY CONTRIBUTIONS')
    b += [line(36, 49, 884, 49), text(36, 89, 'A year, in relief.', 28),
          text(884, 86, f'{total:,}', 28, anchor='end', mono=True),
          text(884, 107, f'CONTRIBUTIONS / {active} ACTIVE DAYS', 10, 'muted', anchor='end', mono=True)]
    weeks = weekly_groups(days)
    # Orthographic projection. Time runs left to right; weekdays run front to back.
    # Logarithmic height preserves quieter days without letting peak days dominate.
    ox, oy, wx, wy, dx, dy = 83, 324, 12.8, -2.35, 15, 7
    def pos(w, d, z=0):
        return ox + w*wx + d*dx, oy + w*wy + d*dy - z
    n = len(weeks)
    b.append(polygon([pos(-.5,-.5),pos(n-.5,-.5),pos(n-.5,6.8),pos(-.5,6.8)], 'plane', 'rule'))
    cells = []
    peak = max(d['count'] for d in days) or 1
    for w, (_, rows) in enumerate(weeks):
        for row in rows:
            d, count = row['date'].weekday(), row['count']
            # Fractional footprint gives every cell its own fine gutter.
            corners = [(w-.02,d-.02),(w+.82,d-.02),(w+.82,d+.82),(w-.02,d+.82)]
            h = 3 + 62*math.log1p(count)/math.log1p(peak) if count else 0
            cells.append((pos(w,d)[1], corners, h, row))
    for _, corners, h, row in sorted(cells, key=lambda c:c[0]):
        flat = [pos(w,d) for w,d in corners]
        raised = [pos(w,d,h) for w,d in corners]
        b.append(f'<g class="enter"><title>{row["date"]}: {row["count"]} contributions</title>')
        if h:
            b.append(polygon([raised[1],raised[2],flat[2],flat[1]], 'side'))
            b.append(polygon([raised[2],raised[3],flat[3],flat[2]], 'front'))
            b.append(polygon(raised, 'accent' if row['count']==peak else 'top', 'grid'))
        else:
            b.append(polygon(flat, 'plane', 'grid'))
        b.append('</g>')
    # A quiet animated survey line follows the footprint; it never consumes cells.
    contour = [pos(-.45,6.95),pos(n-.3,6.95),pos(n-.3,-.45)]
    d = 'M '+' L '.join(f'{x:.2f} {y:.2f}' for x,y in contour)
    b.append(path(d, 'accent', 1.1, extra='class="trace" stroke-dasharray="5 15" opacity=".7"'))
    for idx in (0, n//2, n-1):
        x,y = pos(idx,7.5)
        date = weeks[idx][1][0]['date']
        b.append(text(round(x,2), round(y+18,2), date.strftime('%b %y').upper(), 9, 'muted', mono=True))
    b += [line(36, 428, 884, 428), text(36, 451, 'HEIGHT / LOG(1 + DAILY COUNT)', 10, 'muted', mono=True),
          dot(650,447,2), text(660,451, 'PEAK DAY', 10, 'muted', mono=True),
          text(884,451, f'{peak} CONTRIBUTIONS', 10, 'accent', anchor='end', mono=True)]
    return svg(b, 472, 'Daily GitHub contributions as an architectural terrain',
               f'{total} contributions over 365 days, {active} active days. Each tile is one day; heights use log(1+count). Amber marks the peak count. Counts are not lines of code.')


def signal(days):
    groups = weekly_groups(days)[-8:]
    values = [candle_summary(rows) for _, rows in groups]
    ymax = max(v['high'] for v in values) or 1
    top, bottom, x0, xend = 110, 257, 70, 593
    ys = lambda value: bottom - value/ymax*(bottom-top)
    b = label(31, '02', 'ACTIVITY SIGNAL', '8 WEEKS / DAILY RANGE')
    b += [line(36,49,884,49), text(36,83,'The rhythm behind the work.',23)]
    for frac in (0,.5,1):
        y=ys(ymax*frac)
        b += [line(x0,y,xend,y,'rule',extra='stroke-dasharray="2 6"'),
              text(52,y+4,str(round(ymax*frac)),9,'muted',anchor='end',mono=True)]
    peakweek = max(v['volume'] for v in values) or 1
    for i, ((date, rows), val) in enumerate(zip(groups,values)):
        x=x0+30+i*64
        b.append(f'<g class="enter"><title>Week of {date}: first day {val["open"]}, last day {val["close"]}, daily range {val["low"]}–{val["high"]}, total {val["volume"]}. {len(rows)} observed days.</title>')
        color='accent' if val['close']>=val['open'] and val['volume'] else 'muted'
        b.append(line(x,ys(val['low']),x,ys(val['high']),color,1.5))
        hi,lo=ys(max(val['open'],val['close'])),ys(min(val['open'],val['close']))
        if abs(lo-hi)<2:
            b.append(line(x-8,hi,x+8,hi,color,2))
        else:
            fill=P[color] if val['close']>=val['open'] else P['bg']
            b.append(f'<rect x="{x-8}" y="{hi:.2f}" width="16" height="{lo-hi:.2f}" fill="{fill}" stroke="{P[color]}"/>')
        volh=val['volume']/peakweek*24
        b.append(f'<rect x="{x-8}" y="{292-volh:.2f}" width="16" height="{volh:.2f}" fill="{P["muted"]}" opacity=".35"/>')
        b += [text(x,311,date.strftime('%d %b'),9,'muted',anchor='middle',mono=True),'</g>']
    b += [line(628,110,628,313), text(658,128,'LAST 7 DAYS',10,'muted',mono=True),
          text(658,168,str(sum(d['count'] for d in days[-7:])),32,mono=True),
          text(658,188,'contributions',12,'muted'),
          text(658,229,'LAST 30 DAYS',10,'muted',mono=True),
          text(658,269,str(sum(d['count'] for d in days[-30:])),32,mono=True),
          text(658,289,'contributions',12,'muted'),
          line(36,333,884,333), text(36,356,'WICK / MIN–MAX DAILY COUNT    BODY / FIRST–LAST DAY',9,'muted',mono=True),
          text(884,356,'BELOW / WEEKLY TOTAL',9,'muted',anchor='end',mono=True)]
    return svg(b,378,'Eight-week contribution signal',
               'Each candle represents real daily counts in a Monday-based week: wick=min/max, body=first/last observed day, lower bar=weekly total. The last week can be partial. These are activity counts, not financial prices or a productivity score.')


def projects_header():
    return svg(label(31,'03','SELECTED WORK','APPLICATIONS / AUTOMATION')+[line(36,49,884,49)],65,
               'Selected public projects','Applications and automation projects by valthvn, including attributed forks.')


def project_card(project, i):
    # Entire image is wrapped in a real Markdown/HTML link by README generation.
    b = [text(36,33,f'0{i+1}',11,'accent',mono=True), text(70,33,project['category'],10,'muted',mono=True,spacing=.7),
         text(70,66,project['title'],26,weight=600),
         text(70,95,project['description'],14,'muted'),
         text(70,122,project['detail'],10,'muted',mono=True),
         text(70,145,project['note'],10,'muted'),
         path('M 848 51 L 866 33 M 849 33 L 866 33 L 866 50','accent',1.5),
         line(36,165,884,165)]
    return svg(b,179,project['title'],project['description']+' '+project['note'])


def footer(days, data):
    date=days[-1]['date'].strftime('%d %b %Y').upper()
    updated=data['generated_at'].replace('T',' ').replace('Z',' UTC')
    b=[text(36,32,'04',11,'accent',mono=True),text(70,32,'METHOD / SOURCE',10,'muted',mono=True,spacing=1),
       text(36,68,'Real contributions. Different perspective.',20),
       text(36,96,'Daily public GitHub data / custom SVG / no third-party widgets',11,'muted'),
       text(884,32,'AS OF '+date,10,'muted',anchor='end',mono=True),
       text(36,129,'SNAPSHOT / '+updated,9,'muted',mono=True),
       text(884,129,'VALTHVN / GITHUB',10,'accent',anchor='end',mono=True)]
    return svg(b,151,'Profile method and data timestamp',
               f'Public GitHub contribution counts. Last snapshot fetched {updated}; last observed day {date}. Counts measure activity, not productivity. Source and methodology are linked below.')


def picture(name, alt, href=None):
    image=(f'<picture>\n'
           f'  <source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">\n'
           f'  <source media="(prefers-color-scheme: light)" srcset="./assets/{name}-light.svg">\n'
           f'  <img src="./assets/{name}-dark.svg" width="920" alt="{esc(alt)}">\n'
           f'</picture>')
    return f'<a href="{esc(href)}">\n{image}\n</a>' if href else image


def main():
    global P
    config=json.loads((ROOT/'data/observatory.json').read_text())
    data=json.loads((ROOT/'data/contributions.json').read_text())
    days=normalize_days(data)
    dest=ROOT/'assets'
    dest.mkdir(exist_ok=True)
    for theme,P in PALETTES.items():
        panels={'hero':hero(config,days),'terrain':terrain(days),'signal':signal(days),
                'work':projects_header(),'footer':footer(days,data)}
        panels.update({f'project-{i+1}':project_card(project,i) for i,project in enumerate(config['projects'])})
        for name,content in panels.items():
            (dest/f'{name}-{theme}.svg').write_text(content,encoding='utf-8')
    sections=[picture('hero','valthvn — software, tools and experiments'),
              picture('terrain','365 days of real GitHub contributions, rendered as an architectural terrain.'),
              picture('signal','Weekly candles of daily contribution counts and seven- and thirty-day totals.'),
              picture('work','Selected public work')]
    for i,project in enumerate(config['projects']):
        sections.append(picture(f'project-{i+1}',project['title']+' — '+project['description'],
                                'https://github.com/'+config['username']+'/'+project['repo']))
    sections.append(picture('footer','Real contribution data — methodology and snapshot date.'))
    sections.append('<p align="center">\n  <a href="https://github.com/valthvn?tab=repositories">All repositories</a> · '
                    '<a href="https://github.com/valthvn/valthvn">Source</a> · '
                    '<a href="./docs/observatory.md">How this profile works</a>\n</p>')
    (ROOT/'README.md').write_text('<!-- Generated by scripts/render_observatory.py. Edit data/observatory.json for copy and projects. -->\n\n'
                                +'\n\n'.join(sections)+'\n',encoding='utf-8')
    print(f'Rendered {len(panels)*2} themed panels: {sum(d["count"] for d in days)} real contributions, '
          f'{days[0]["date"]} to {days[-1]["date"]}.')


if __name__=='__main__':
    main()
