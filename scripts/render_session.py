#!/usr/bin/env python3
"""An animated monochrome shell session, using existing portrait and calendar data."""
import json
import xml.etree.ElementTree as ET
from functools import partial
from pathlib import Path
from render_desktop import text, rect, svg, PROJECTS
from render_observatory import normalize_days

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'assets/session'
T = partial(text, fill='#f0f0f0')
R = partial(rect, stroke='none', sw=0)
STYLE = '''<style>
@keyframes type{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes enter{from{opacity:0}to{opacity:1}}
@keyframes cursor{50%{opacity:0}}
.type{animation:type 1.1s steps(34,end) both}
.output{animation:enter .5s both}
.cursor{animation:cursor 1s step-end infinite}
@media(prefers-reduced-motion:reduce){.type,.output,.cursor{animation:none}}
</style>'''


def reveal(body, delay, kind='output'):
    return f'<g class="{kind}" style="animation-delay:{delay}s">{body}</g>'


def shell(body, height, title, desc, animated=True):
    return svg(960, height, title, desc, (STYLE if animated else '')+R(0,0,960,height,'#0b0b0b')+body)


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
    art = ''.join(T(0,8+i*6.2,node.text or '',6.2) for i,node in enumerate(portrait))
    b += reveal('<g transform="translate(558 212)" xml:space="preserve">'+art+'</g>',2.6)
    b += reveal(T(34,525,'~ $ ./explore',16),4.8,'type')
    b += reveal(T(34,556,'projects/      stack.json      activity.log',13,fill='#b8b8b8'),6)
    b += reveal(T(34,596,'~ $',16)+'<rect class="cursor" x="77" y="582" width="10" height="18" fill="#f0f0f0"/>',6.4)
    b += R(32,622,896,1,'#393939')+T(34,650,'END OF BOOT / YOUR NEXT COMMAND IS BELOW ↓',11,fill='#969696')
    return shell(b,676,'VALTHVN — a living terminal session',
                 'Animated connection and whoami sequence with Valentin’s ASCII portrait. Vibe coder; '
                 'web applications, tools and APIs. Build, learn, iterate. Project links and expandable stack follow.')


def project(label,repo,number,color):
    b = T(26,32,number,12,fill='#969696')+T(74,33,'cd ~/projects/'+repo,17)
    b += T(74,62,'OPEN REPOSITORY',10,fill='#969696')+T(895,48,'↗',26)
    b += R(26,81,908,1,'#393939')
    return shell(b,90,'Open '+label,'Shell-style link to the '+label+' repository.',False)


def activity(data):
    days = normalize_days(data)
    recent = days[-90:]
    total = sum(d['count'] for d in days)
    b = T(32,39,'~ $ git activity --last 90d --draw',17)
    b += T(32,75,'ONE COLUMN = ONE OBSERVED DAY / HEIGHT = CONTRIBUTIONS',10,fill='#969696')
    peak = max(1,max(d['count'] for d in recent))
    for i,d in enumerate(recent):
        h = 116*d['count']/peak
        bar = (f'<g data-date="{d["date"]}" data-count="{d["count"]}">'
               f'<title>{d["date"]}: {d["count"]} contributions</title>'
               +R(33+i*10,218-max(2,h),5,max(2,h),'#eeeeee' if d['count'] else '#353535')+'</g>')
        b += reveal(bar,i*.025)
    b += T(32,246,str(recent[0]['date']),11,fill='#969696')+T(821,246,str(recent[-1]['date']),11,fill='#969696')
    b += R(32,270,896,1,'#393939')
    b += T(32,307,total,30,weight=700)+T(145,305,'CONTRIBUTIONS / 365 DAYS',11)
    b += T(505,307,sum(d['count'] for d in recent),30,weight=700)+T(620,305,'CONTRIBUTIONS / 90 DAYS',11)
    b += T(32,341,'PUBLIC CALENDAR SNAPSHOT / '+data['generated_at'],10,fill='#969696')
    return shell(b,366,'Real GitHub contributions — 90-day activity trace',
                 f'{total} contributions in 365 observed days; {sum(d["count"] for d in recent)} in the last 90. '
                 f'One column per day from {recent[0]["date"]} to {recent[-1]["date"]}. '
                 'Counts are contributions, not exclusively commits. Zero days use a dim baseline.')


def readme():
    links = '\n'.join(f'<a href="https://github.com/valthvn/{repo}"><img src="./assets/session/project-{number}.svg" width="960" alt="Open {label} repository"></a><br>'
                      for label,repo,number,_ in PROJECTS)
    return '''<!-- VALTHVN / SESSION 005 -->

<img src="./assets/session/boot.svg" width="960" alt="VALTHVN. Animated monochrome terminal and ASCII portrait. Valentin / valthvn — vibe coder, building web applications, tools and APIs. Build. Learn. Iterate.">

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

<img src="./assets/session/activity.svg" width="960" alt="Real public GitHub activity: 90 daily columns, totals over 365 and 90 observed days, and dated snapshot. Contributions include more than commits.">

<details>
<summary><code>~ $ help</code></summary>

`projects/` — click a repository row above.  
`stack.json` — expand the toolbox.  
`activity.log` — real public contribution counts, refreshed daily.  
`history` — [saved editions v1 / v2 / v3 / v4 / v5](./docs/versions.md).  
`ls -a` — [all repositories](https://github.com/valthvn?tab=repositories).  
`man session` — [how this profile works](./docs/session.md).

</details>
'''


def main():
    data = json.loads((ROOT/'data/contributions.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'boot.svg').write_text(hero(),encoding='utf-8')
    (OUT/'activity.svg').write_text(activity(data),encoding='utf-8')
    for project_data in PROJECTS:
        (OUT/f'project-{project_data[2]}.svg').write_text(project(*project_data),encoding='utf-8')
    (ROOT/'README.md').write_text(readme(),encoding='utf-8')
    print('Rendered SESSION 005: animated boot, repository commands and real activity.')


if __name__ == '__main__':
    main()
