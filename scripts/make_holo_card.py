#!/usr/bin/env python3
"""Native vector design of a personal full-art collectible card.

The artwork is an original bird mascot referencing the profile's existing bird
identity. HP and move values are fictional card decoration, not GitHub scores.
"""
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def text(x,y,value,size=12,fill='#eaf7ff',weight=400,extra=''):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}" {extra}>{value}</text>'


def make_card():
    b=['<svg xmlns="http://www.w3.org/2000/svg" width="440" height="616" viewBox="0 0 440 616" role="img" aria-labelledby="title desc">',
       '<title id="title">VALTHVN EX — personal holographic collectible card</title>',
       '<desc id="desc">A Pokémon-inspired full-art bird card. Workflow Link ability; Build and Iterate move. HP infinity is fictional decorative card data.</desc>',
       '''<defs>
       <linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffe9a1"/><stop offset=".18" stop-color="#9ddfff"/><stop offset=".42" stop-color="#b89ee7"/><stop offset=".63" stop-color="#ffdf93"/><stop offset=".83" stop-color="#9febda"/><stop offset="1" stop-color="#f7f0be"/></linearGradient>
       <linearGradient id="face" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#182334"/><stop offset=".55" stop-color="#1c2237"/><stop offset="1" stop-color="#101a27"/></linearGradient>
       <radialGradient id="cosmos"><stop stop-color="#24406b"/><stop offset=".55" stop-color="#1c284d"/><stop offset="1" stop-color="#091420"/></radialGradient>
       <linearGradient id="feather" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#303a55"/><stop offset=".6" stop-color="#11182b"/><stop offset="1" stop-color="#536c8c"/></linearGradient>
       <linearGradient id="silver" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#f0fcff"/><stop offset=".45" stop-color="#bddcee"/><stop offset=".7" stop-color="#efffff"/><stop offset="1" stop-color="#8bacc8"/></linearGradient>
       <clipPath id="art"><rect x="27" y="89" width="386" height="262" rx="9"/></clipPath>
       </defs>''',
       '<rect x="1" y="1" width="438" height="614" rx="24" fill="url(#edge)"/>',
       '<rect x="7" y="7" width="426" height="602" rx="20" fill="url(#face)" stroke="#fff8d3" stroke-opacity=".45"/>',
       '<rect x="14" y="14" width="412" height="588" rx="15" fill="none" stroke="url(#edge)" stroke-width=".8"/>',
       text(28,35,'BASIC',10,'#dec68f',700,extra='letter-spacing="1.6"'),
       text(28,65,'VALTHVN',32,'#f5f4dd',700,extra='letter-spacing="-1"'),
       text(211,65,'EX',25,'#efcf8c',700,extra='font-style="italic"'),
       text(322,62,'HP',11,'#ecdfae',700),text(343,65,'∞',27,'#f8e6ae',700),
       '<circle cx="400" cy="54" r="13" fill="#7fb9d1" stroke="#d8efff" stroke-width="1.5"/>',
       '<path d="M400 45 L394 55 L400 63 L406 55 Z" fill="#192c47"/>',
       '<g clip-path="url(#art)"><rect x="27" y="89" width="386" height="262" fill="url(#cosmos)"/>']
    rng=random.Random(140728642)
    for i in range(85):
        x,y=rng.uniform(30,410),rng.uniform(91,348)
        r=rng.choice([.5,.65,.85,1.1])
        b.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#d5eaff" opacity="{rng.uniform(.2,.8):.2f}"/>')
    b += [
       '<path d="M40 302 Q240 30 408 205 M42 335 Q196 54 400 157" fill="none" stroke="#78bac9" stroke-opacity=".15" stroke-width="1.5"/>',
       '<ellipse cx="226" cy="229" rx="130" ry="103" fill="none" stroke="#88bcdf" stroke-opacity=".22"/>',
       '<ellipse cx="226" cy="229" rx="146" ry="73" fill="none" stroke="#df98c7" stroke-opacity=".22" transform="rotate(-34 226 229)"/>',
       # Angular rear wing, silhouetted against the sky.
       '<path d="M227 196 Q281 216 354 309 L318 301 L334 329 L296 314 L305 340 L258 317 L209 260 Z" fill="url(#feather)" stroke="#8ab9d5" stroke-width="2"/>',
       '<path d="M248 227 L317 293 M240 243 L301 303 M231 259 L283 307" fill="none" stroke="#7d9fbf" stroke-opacity=".6"/>',
       # White breast, dark head and distinctive blade-like beak.
       '<path d="M174 174 Q209 158 240 196 Q255 224 242 250 Q249 280 282 310 Q256 341 214 350 L161 350 Q130 324 139 283 Q148 254 169 220 Z" fill="url(#silver)" stroke="#aac4d8" stroke-width="1.8"/>',
       '<path d="M155 152 Q151 105 187 106 Q220 105 243 146 Q260 178 245 202 L230 226 Q205 201 190 203 L172 231 L157 208 L140 177 Z" fill="url(#feather)" stroke="#b3d7e6" stroke-width="2"/>',
       '<path d="M178 166 L139 179 L146 222 L163 251 L175 207 Z" fill="#172134" stroke="#7dacc8" stroke-width="1.5"/>',
       '<path d="M164 175 Q159 199 157 220 L164 234" fill="none" stroke="#e4faff" stroke-width="3" stroke-linecap="round"/>',
       '<path d="M175 192 Q197 179 205 151" fill="none" stroke="#f1fbff" stroke-width="2" stroke-linecap="round"/>',
       '<path d="M153 183 L164 180 L159 186 Z" fill="#e4f8ff"/>',
       '<circle cx="190" cy="157" r="4.5" fill="#1e304c"/><circle cx="190" cy="157" r="2.1" fill="#e4ffff"/>',
       '<path d="M239 221 Q255 243 223 265 L205 256 Q228 245 224 231" fill="#17253c" stroke="#7897b4"/>',
       '<path d="M147 294 Q172 313 180 349 M214 273 Q198 316 209 349" stroke="#a3c2d7" stroke-width="1.2" fill="none" opacity=".6"/>',
       # Decorative star glints.
       '<path d="M324 126 V146 M314 136 H334 M329 131 L319 141 M319 131 L329 141" stroke="#c5f2ff" stroke-width="1.2"/>',
       '<path d="M86 244 V260 M78 252 H94" stroke="#e8c8fa" stroke-width="1.2"/>',
       '</g><rect x="27" y="89" width="386" height="262" rx="9" fill="none" stroke="url(#edge)" stroke-width="2"/>',
       '<rect x="33" y="339" width="180" height="19" rx="8" fill="#1a2b3d" stroke="#96bdd0" stroke-width=".65"/>',
       text(44,352,'CREATIVE CODER / FULL ART',8.8,'#d8e8f3',700,extra='letter-spacing=".6"'),
       '<rect x="30" y="372" width="67" height="21" rx="10" fill="#b75282"/>',text(42,387,'Ability',12,'#ffffff',700),
       text(109,389,'Workflow Link',21,'#efdaaa',700),
       text(33,415,'Connect tools. Reduce friction. Keep building.',12,'#c8d6e3'),
       '<line x1="32" y1="434" x2="408" y2="434" stroke="#6d89a0" stroke-opacity=".5"/>',
       '<circle cx="42" cy="463" r="11" fill="#d8e6ec"/><path d="M42 455 L36 466 H48 Z" fill="#334664"/>',
       '<circle cx="69" cy="463" r="11" fill="#a7a9db"/><path d="M69 455 V471 M63 463 H75" stroke="#1d2946" stroke-width="2"/>',
       text(97,471,'Build &amp; Iterate',23,'#f5f0d8',700),text(381,472,'∞',24,'#ecdfb6',700),
       text(33,499,'Apps, automation and careful details.',13,'#d6e3ea'),
       text(33,521,'C# / Python / TypeScript / JavaScript',11,'#9eb6cc'),
       '<line x1="31" y1="540" x2="409" y2="540" stroke="#6d89a0" stroke-opacity=".5"/>',
       text(32,559,'weakness',8,'#b6c5d2'),text(88,559,'bugs ×2',10,'#ebdcba',700),
       text(165,559,'resistance',8,'#b6c5d2'),text(225,559,'routine −30',10,'#ebdcba',700),
       text(320,559,'retreat',8,'#b6c5d2'),text(358,559,'coffee',10,'#ebdcba',700),
       text(32,589,'VALTHVN / V3',9,'#bbcee0',700,extra='letter-spacing=".6"'),
       text(252,589,'CUSTOM PROMO 003/003 ★',9,'#eed9a3',700),
       '</svg>']
    return ''.join(b)+'\n'


if __name__=='__main__':
    dest=ROOT/'assets/holo/card-front.svg'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(make_card(),encoding='utf-8')
    print('Wrote original vector full-art card.')
