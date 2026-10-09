# VALTHVN OS — v4

A completely different edition: a static personal desktop in mint, cream and warm yellow. A menu bar, original pixel bird, windows, terminal and folder shortcuts replace the collectible card and activity dashboard.

The original SVG illustration is generated with Python's standard library. It uses local fonts, text and vector shapes, with no scripts, remote fonts or external image services. It is static and needs no reduced-motion variant. The three folder images link to the actual repositories through HTML anchors. Illustrated window controls are decorative.

On narrow screens GitHub scales the illustration down. Project shortcuts wrap; the toolbox remains selectable Markdown. Alternative text carries the introduction independently of the illustration. The toolbox and introduction use existing profile information; no statistics or new personal claims are invented.

## Design assumptions

No external reference was supplied. Familiar desktop conventions inform an original composition: square window frames, compact title bars, consistent spacing and restrained colors. Dark green provides contrast against light surfaces. HTML links below the illustration provide navigation.

## Rebuild

```sh
python scripts/render_desktop.py
python -m unittest discover -s tests -q
```

No third-party library is needed to render this edition. The workflow validates and regenerates the static assets on source changes. A daily refresh is unnecessary because no live counters are displayed. Earlier artwork, renderers and snapshot branches remain available.
