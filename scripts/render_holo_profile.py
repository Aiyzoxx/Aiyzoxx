#!/usr/bin/env python3
"""Daily profile data and clickable project links around the saved holo animation."""
import html
import json
from pathlib import Path
from render_observatory import normalize_days

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'assets/holo'


def text(x,y,value,size=12,fill='#bed0e2',anchor='start',weight=400):
    return (f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{html.escape(str(value))}</text>')


def svg(body,w,h,title,desc):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="title description"><title id="title">{html.escape(title)}</title>'
            f'<desc id="description">{html.escape(desc)}</desc>'
            f'<rect width="{w}" height="{h}" rx="14" fill="#0e1421"/>'+''.join(body)+'</svg>\n')


def ledger(data,days):
    total=sum(d['count'] for d in days)
    recent=sum(d['count'] for d in days[-90:])
    active=sum(d['count']>0 for d in days)
    end=days[-1]['date'].strftime('%d %b %Y').upper()
    b=[text(30,29,'REAL GITHUB ACTIVITY',10,'#89c6e6',weight=700),
       text(890,29,'HOLO EX / V3',10,'#b7a1db','end',700)]
    for x,value,label in [(30,total,'CONTRIBUTIONS / 365 DAYS'),(340,recent,'CONTRIBUTIONS / 90 DAYS'),(650,active,'ACTIVE DAYS / 365 DAYS')]:
        b += [text(x,75,str(value),29,'#ecf6ff',weight=700),text(x,98,label,10,'#a0b5c8')]
    b += [text(30,136,'PUBLIC SNAPSHOT / '+data['generated_at'].replace('T',' ').replace('Z',' UTC'),9,'#9badc0'),
          text(890,136,'AS OF '+end,9,'#9badc0','end')]
    return svg(b,920,157,'Real public GitHub contribution activity',
               f'{total} contributions in 365 observed days; {recent} in 90 days; {active} active days. '
               f'Last observed day {end}. These are real public-calendar counts; HP and move values on the artwork are fictional.')


def project_tile(project,i):
    b=[f'<rect x=".5" y=".5" width="299" height="83" rx="13" fill="none" stroke="#43506b"/>',
       text(18,25,f'0{i+1} / OPEN PROJECT',9,'#9ab8d6'),text(18,56,project['label'],21,'#f0f6fb',weight=600),
       '<path d="M274 23 L286 11 M274 11 H286 V23" fill="none" stroke="#a8c8fa" stroke-width="1.5"/>']
    return svg(b,300,84,project['label'],f'Open the public repository for {project["label"]}.')


def main():
    config=json.loads((ROOT/'data/holo.json').read_text())
    data=json.loads((ROOT/'data/contributions.json').read_text())
    days=normalize_days(data)
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'ledger.svg').write_text(ledger(data,days),encoding='utf-8')
    project_links=[]
    for i,project in enumerate(config['projects']):
        name=f'project-{i+1}.svg'
        (DEST/name).write_text(project_tile(project,i),encoding='utf-8')
        href='https://github.com/'+config['username']+'/'+project['repo']
        project_links.append(f'<a href="{html.escape(href,quote=True)}"><img src="./assets/holo/{name}" width="300" alt="{html.escape(project["label"],quote=True)} — open project"></a>')
    readme='''<!-- HOLO EX / V3 — profile animation and daily public data -->

<p align="center">
<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/holo/profile-still.png">
  <source type="image/webp" srcset="./assets/holo/profile.webp">
  <img src="./assets/holo/profile.gif" width="720" alt="VALTHVN EX: a Pokémon-inspired full-art bird card tilts in perspective, with moving rainbow foil, specular glints and a colored glow. The movement loops automatically.">
</picture>
</p>

<p align="center">
'''+ '\n'.join(project_links)+'''
</p>

<img src="./assets/holo/ledger.svg" width="920" alt="Real public GitHub contributions over 365 and 90 observed days, active days and snapshot date.">

<p align="center">
  <a href="https://github.com/valthvn?tab=repositories">All repositories</a> · <a href="./docs/holo.md">How the holo works</a> · <a href="./docs/versions.md">Saved versions: v1 / v2 / v3</a>
</p>
'''
    (ROOT/'README.md').write_text(readme,encoding='utf-8')
    print(f'Rendered Holo EX / v3: {sum(d["count"] for d in days)} real annual contributions; saved animation retained.')


if __name__=='__main__':
    main()
