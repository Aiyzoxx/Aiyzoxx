# Édition — volume 02

A profile designed as a software journal. Paper, black ink and cobalt, with an asymmetrical layout, a halftone bird avatar, real application captures and a small activity trace at the end.

The paper palette is intentional in both GitHub themes. The SVG panels have their own background, so their typography and screenshot annotations retain the same contrast.

## Sources and attribution

The project captures are preserved byte-for-byte from their public repositories, then embedded as PNG data inside each SVG. Their values are examples from those captures, not live temperature, usage or quota data. No external image requests occur when the SVG is displayed.

- [Mint](https://github.com/valthvn/Mint): `docs/screenshots/dashboard.png` and `settings.png`. Mint builds on Universal x86 Tuning Utility; see the project's license and credits.
- [ValthvnQuota](https://github.com/valthvn/ValthvnQuota): `docs/screenshots/taskbar_both.png` and `flyout_antigravity.png`. A fork of CodexQuota extended with Antigravity support; see the project's license and credits.
- [Antigravity RPC](https://github.com/valthvn/antigravity-discord-rpc): the drawing is a workflow schematic, not a screenshot or live status. Its example `Project: Mint / Editing code` illustrates the process watcher and Discord Rich Presence integration.
- The bird artwork uses the existing `ascii-portrait.svg`: its 100 × 53 character density grid is mapped to native SVG dots. The underlying source is not replaced and no new person or avatar is invented.

Local screenshot filenames, original URLs and Git blob hashes are recorded in `assets/edition/source/sources.json`.

## Field notes

The activity trace uses exactly the last 90 observed daily contribution counts from `data/contributions.json`. The profile shows their sum and ending date. Height is scaled by `log(1 + count)` to preserve quieter days. Empty days remain real zeros.

The contribution parser validates dates and counts before replacing a snapshot. If GitHub's public calendar changes or a request fails, the workflow stops and the last valid profile remains available. The last observed date stays visible. The count is GitHub contribution activity, not commits alone or a productivity score. No private repository names are requested.

The line-drawing effects and status dot are decorative. They run without JavaScript and are disabled for `prefers-reduced-motion`. Every panel has a static state, an SVG title and description, and an HTML alt text. Project destinations are links around whole images.

## Updating

The workflow **Update profile edition** runs daily at 06:17 UTC, when its source files change, or manually. Scheduled runs may be delayed by GitHub. It fetches the calendar, renders the five panels and commits changes on the default branch. No personal token, package install, external widget or paid service is needed.

Python 3.11 or later:

```sh
python -m unittest discover -s tests -v
python scripts/fetch_contributions.py
python scripts/render_edition.py
python -m unittest discover -s tests -v
```

An offline render can use the committed contribution snapshot. Edit `data/edition.json` for identity text, stack and project links; visual layout and article copy live in `scripts/render_edition.py`. The older observatory renderer remains available for reproducing v1.

See [version history](versions.md) for the saved profiles and restoration approach.
