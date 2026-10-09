# Holo EX — v3

An original Pokémon-inspired collectible card for valthvn, built around the existing bird identity. The complete card changes perspective, while rainbow foil, a diagonal specular highlight, tiny glints and a colored halo respond to its viewing angle.

The card is an original vector design, not a screenshot of an official card. HP infinity, move values, weaknesses and rarity markings are fictional visual elements. Real GitHub contribution counts are shown separately below it. The three project tiles are actual links to public repositories.

## Actual motion

The motion is a rendered animation, not a static card with a CSS glow:

- The full-resolution animated WebP has 96 frames in a seamless 7.68-second loop.
- Each frame rotates the card with yaw, pitch and roll in three dimensions, then projects its four corners using a perspective camera.
- An inverse homography maps the entire card surface to that quadrilateral. Header, artwork and ability text all move together.
- A changing spectral layer and specular light band are projected with the face. Foil is strongest on the art and metallic border and gentler over body text.
- The outer glow follows the projected silhouette and changes color and intensity with the angle.

On GitHub the effect plays automatically. It does not track the pointer: the README displays images, without a JavaScript interaction layer. A smaller 48-frame GIF is available as a browser fallback. The picture element selects a static PNG for `prefers-reduced-motion: reduce`.

## Saved design, live activity

The artwork contains no live counters. The animation is generated once per visual edition and committed with that edition. The daily job retains the animation and updates only the ledger, project links and public contribution data. A calendar outage leaves the previous validated data and its date visible.

The annual ledger uses exactly 365 consecutive observed days. Its second counter uses the last 90 of them. Counts are GitHub contributions, not exclusively commits or a productivity score. No private repository names are accessed.

## Source and reproduction

- `scripts/make_holo_card.py` creates the original native SVG design.
- `assets/holo/card-front.svg` is the vector master; `card-front.png` is its 440 × 616 transparent raster export.
- `scripts/animate_holo_card.py` renders perspective, light and glow using Pillow and a small standard-library homography solver.
- `assets/holo/animation.json` records frame counts, dimensions and timing.
- `scripts/render_holo_profile.py` updates the README and contribution ledger without touching the saved animation.

To rebuild the animation, generate the vector front, rasterize it at 440 × 616 while preserving transparency, then run the encoder. An SVG renderer such as Sharp can perform the raster export. No AI-generated raster artwork or outside card template is used.

```sh
python -m pip install -r scripts/requirements-holo.txt
python scripts/make_holo_card.py
# Raster export: card-front.svg -> card-front.png, 440 x 616, transparent.
python scripts/animate_holo_card.py
python scripts/render_holo_profile.py
python -m unittest discover -s tests -v
```

The automatic workflow fetches GitHub's public calendar daily at 06:17 UTC or on relevant pushes/manual dispatch. It tests source integrity, actual multi-frame animation, perspective geometry, reduced-motion selection, links and data semantics before committing the updated ledger.

The previously saved profiles remain available on the [version branches](versions.md).
