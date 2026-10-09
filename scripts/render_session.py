#!/usr/bin/env python3
"""An animated monochrome shell session, using existing portrait and calendar data."""
import datetime as dt
import html
import json
import math
from html import escape
import xml.etree.ElementTree as ET
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/session'
PROJECTS = [('Mint', 'Mint', '01'), ('ValthvnQuota', 'ValthvnQuota', '02'),
            ('SkyHands', 'SkyHands', '03')]


def rect(x, y, w, h, fill, stroke='#f0f0f0', sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def text(x, y, value, size=14, fill='#f0f0f0', weight=400, family='monospace'):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{html.escape(str(value))}</text>')


def svg(w, h, title, description, body):
    result = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
              f'role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title>'
              f'<desc id="desc">{html.escape(description)}</desc>{body}</svg>\n')
    ET.fromstring(result)
    return result


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


T = partial(text, fill='#f0f0f0')
R = partial(rect, stroke='none', sw=0)
STYLE = '''<style>
@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes enter{from{opacity:0}to{opacity:1}}
@keyframes cursor{50%{opacity:0}}
@keyframes portrait-print{from{width:0}to{width:372px}}
@keyframes portrait-scan{from{transform:translateX(0);opacity:1}to{transform:translateX(372px);opacity:1}}
.type{animation:type 1.1s steps(34,end) both}
.output{animation:enter .5s both}
.cursor{animation:cursor 1s step-end infinite}
.portrait-clip{animation:portrait-print var(--row-duration) steps(100,end) var(--row-delay) both}
.portrait-cursor{opacity:0;animation:portrait-scan var(--row-duration) linear var(--row-delay)}
@media(prefers-reduced-motion:reduce){.type,.output,.cursor,.portrait-clip,.portrait-cursor{animation:none}.portrait-clip{width:372px}.portrait-cursor{display:none}}
</style>'''


def reveal(body, delay, kind='output'):
    return f'<g class="{kind}" style="animation-delay:{delay}s">{body}</g>'


def shell(body, height, title, desc, animated=True):
    return svg(960, height, title, desc, (STYLE if animated else '')+body)


def hero():
    b = T(32,35,'●  PUBLIC SESSION',11)+T(733,35,'TTY / 005   UTF-8',11)
    b += R(32,53,896,1,'#393939')
    b += T(27,142,'VALTHVN',100,weight=700,family='Arial,Helvetica,sans-serif')
    b += T(33,177,'SOFTWARE, FROM THE OTHER SIDE OF THE PROMPT.',12)
    b += reveal(T(34,232,'~ $ ssh valthvn@github',16),0,'type')
    b += reveal(T(34,262,'Connection established. Welcome to my corner.',12,fill='#b8b8b8'),1.2)
    b += reveal(T(34,310,'~ $ whoami --verbose',16),1.8,'type')
    rows = [('user','Valentin / valthvn'),('role','Vibe coder'),('focus','Web applications, tools & APIs'),
            ('mindset','Build. Learn. Iterate.'),('source','Open source. Always curious.')]
    for i,(key,value) in enumerate(rows):
        b += reveal(T(34,351+i*28,key,12,fill='#969696')+T(135,351+i*28,value,12),3+i*.2)
    portrait = ET.parse(ROOT/'ascii-portrait.svg').getroot().findall('.//{http://www.w3.org/2000/svg}text')[1:-1]
    art = ''
    for i,node in enumerate(portrait):
        timing = f'--row-duration:{5.8/len(portrait):.6f}s;--row-delay:{2.6+i*5.8/len(portrait):.6f}s'
        baseline = 8+i*6.2
        art += (f'<defs><clipPath id="portrait-row-{i}"><rect class="portrait-clip" '
                f'x="0" y="{baseline-5.2}" width="372" height="6.2" style="{timing}"/></clipPath></defs>')
        characters = [(column,char) for column,char in enumerate(node.text or '') if char != ' ']
        if characters:
            # Explicit glyph positions survive SVG renderers collapsing leading spaces.
            positions = ' '.join(f'{column*3.72:.2f}' for column,_ in characters)
            art += f'<g clip-path="url(#portrait-row-{i})">'+T(positions,baseline,''.join(char for _,char in characters),6.2)+'</g>'
        art += f'<rect class="portrait-cursor" x="0" y="{baseline-5.2}" width="3.72" height="6.2" fill="#f0f0f0" style="{timing}"/>'
    b += '<g transform="translate(558 212)" xml:space="preserve">'+art+'</g>'
    b += reveal(T(34,525,'~ $ ./explore',16),8.6,'type')
    b += reveal(T(34,556,'projects/      stack.json      activity.log',13,fill='#b8b8b8'),9.8)
    b += reveal(T(34,596,'~ $',16)+'<rect class="cursor" x="77" y="582" width="10" height="18" fill="#f0f0f0"/>',10.2)
    b += R(32,622,896,1,'#393939')+T(34,650,'END OF BOOT / YOUR NEXT COMMAND IS BELOW ↓',11,fill='#969696')
    return shell(b,676,'VALTHVN — a living terminal session',
                 'Animated connection and whoami sequence with Valentin’s ASCII portrait. Vibe coder; '
                 'web applications, tools and APIs. Build, learn, iterate. Project links and expandable stack follow.')


def project(label,repo,number):
    b = T(26,32,number,12,fill='#969696')+T(74,33,'cd ~/projects/'+repo,17)
    b += T(74,62,'OPEN REPOSITORY',10,fill='#969696')+T(895,48,'↗',26)
    b += R(26,81,908,1,'#393939')
    return shell(b,90,'Open '+label,'Shell-style link to the '+label+' repository.',False)


def candles(days):
    result = []
    for i in range(len(days)-90,len(days)):
        opening = sum(d['count'] for d in days[i-7:i])
        closing = sum(d['count'] for d in days[i-6:i+1])
        result.append(dict(date=days[i]['date'],count=days[i]['count'],open=opening,close=closing,
                           high=max(opening,closing),low=min(opening,closing)))
    return result


def activity(data):
    days = normalize_days(data)
    series = candles(days)
    last = series[-1]
    total = sum(d['count'] for d in days)
    recent_total = sum(c['count'] for c in series)
    step = max(1,math.ceil(max(c['high'] for c in series)/4))
    ceiling = step*4
    peak_volume = max(1,max(c['count'] for c in series))
    def y(value):
        return 334-184*value/ceiling
    b = T(32,39,'~ $ git activity --candles',17)
    b += T(32,70,'1D / ROLLING 7D TOTAL / LAST 90 DAYS',11,fill='#969696')
    b += T(32,116,last['close'],34,weight=700)+T(125,113,'CONTRIBUTIONS / LAST 7D',11)
    b += T(550,87,f'O {last["open"]}   H {last["high"]}   L {last["low"]}   C {last["close"]}',12)
    b += T(550,113,'FILLED: UP / HOLLOW: DOWN / LINE: FLAT',10,fill='#969696')
    for value in range(0,ceiling+1,step):
        b += R(32,y(value),830,1,'#252525')+T(884,y(value)+4,value,10,fill='#969696')
    b += R(872,141,1,290,'#393939')
    b += f'<path d="M32 {y(last["close"])} H872" fill="none" stroke="#b8b8b8" stroke-dasharray="3 5"/>'
    b += R(879,y(last['close'])-10,49,20,'#f0f0f0')+T(886,y(last['close'])+4,last['close'],11,fill='#0b0b0b')
    b += T(32,366,'VOL / DAILY CONTRIBUTIONS',10,fill='#969696')
    for i,c in enumerate(series):
        x = 36+i*9.2
        color = '#eeeeee' if c['close']>=c['open'] else '#969696'
        top,bottom = y(c['high']),y(c['low'])
        body = f'<path d="M{x} {top} V{bottom}" stroke="{color}"/>'
        if c['open']==c['close']:
            body += f'<path d="M{x-2.7} {top} H{x+2.7}" stroke="{color}"/>'
        else:
            body += rect(x-2.7,top,5.4,bottom-top,'#eeeeee' if c['close']>c['open'] else 'none',color,1)
        if c['count']:
            h = 46*c['count']/peak_volume
            body += R(x-2.7,425-h,5.4,h,color)
        attributes = ' '.join(f'data-{key}="{c[key]}"' for key in ('date','count','open','high','low','close'))
        body = f'<g {attributes}><title>{c["date"]}: {c["count"]} contributions; rolling 7D O {c["open"]}, H {c["high"]}, L {c["low"]}, C {c["close"]}</title>'+body+'</g>'
        b += reveal(body,i*.025)
    for i in (0,30,60,89):
        b += T(32+i*9.2-(45 if i==89 else 0),450,str(series[i]['date']),10,fill='#969696')
    b += R(32,472,896,1,'#393939')
    b += T(32,510,total,30,weight=700)+T(145,508,'CONTRIBUTIONS / 365 DAYS',11)
    b += T(505,510,recent_total,30,weight=700)+T(620,508,'CONTRIBUTIONS / 90 DAYS',11)
    b += T(32,546,'PUBLIC CALENDAR SNAPSHOT / '+data['generated_at'],10,fill='#969696')
    return shell(b,570,'Real GitHub activity — monochrome contribution candles',
                 f'{total} contributions in 365 observed days; {recent_total} in the last 90. '
                 'Daily candles: open is the previous trailing seven-day total; close is the current total. '
                 'High and low are the larger and smaller endpoints, without invented intraday movement. '
                 'Filled bodies rise, hollow bodies fall, lines are flat. Volume is each day’s actual count.')


def picture(name, alt):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/session/{name}.svg">'
            f'<img src="./assets/session/{name}-light.svg" width="960" alt="{escape(alt,quote=True)}"></picture>')


def readme():
    links = '\n'.join(f'<a href="https://github.com/valthvn/{repo}">'+picture('project-'+number,'Open '+label+' repository')+'</a><br>'
                      for label,repo,number in PROJECTS)
    return '''<!-- VALTHVN / SESSION 005 -->

'''+picture('boot','VALTHVN. Animated monochrome terminal and ASCII portrait. Valentin / valthvn — vibe coder, building web applications, tools and APIs. Build. Learn. Iterate.')+'''

'''+links+'''

<details>
<summary><code>~ $ cat stack.json</code></summary>

```json
{
  "languages": ["Python", "TypeScript", "JavaScript"],
  "frontend": ["React", "Next.js", "Tailwind CSS"],
  "backend": ["FastAPI", "Node.js", "Express"],
  "tools": ["Docker", "Git", "Linux", "GitHub Actions"]
}
```

</details>

<br>

'''+picture('activity','Monochrome GitHub contribution candles: 90 daily candles based on rolling seven-day totals, actual daily volumes, and totals over 365 and 90 observed days. Filled candles rise; hollow candles fall.')+'''

<details>
<summary><code>~ $ help</code></summary>

`projects/` — click a repository row above.  
`stack.json` — expand the toolbox.  
`activity.log` — real public contribution candles, refreshed daily.

</details>
'''


def main():
    data = json.loads((ROOT/'data/contributions.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True,exist_ok=True)
    assets = {'boot':hero(),'activity':activity(data)}
    assets.update((f'project-{p[2]}',project(*p)) for p in PROJECTS)
    for name,body in assets.items():
        (OUT/f'{name}.svg').write_text(body,encoding='utf-8')
        for dark,light in {'#f0f0f0':'#1f2328','#eeeeee':'#1f2328','#b8b8b8':'#59636e',
                           '#969696':'#59636e','#393939':'#d1d9e0','#252525':'#d8dee4','#0b0b0b':'#ffffff'}.items():
            body = body.replace(dark,light)
        (OUT/f'{name}-light.svg').write_text(body,encoding='utf-8')
    (ROOT/'README.md').write_text(readme(),encoding='utf-8')
    print('Rendered SESSION 005: animated boot, repository commands and real activity.')


if __name__ == '__main__':
    main()
