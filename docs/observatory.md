# Profile observatory

A personal engineering log: a small set of custom visualizations using one palette, one typographic system and actual public GitHub contribution counts. There are no external widget services or browser scripts.

## Reading the visualizations

- **Fingerprint:** the last 90 observed days arranged clockwise from the top. One radial mark per day; length is scaled by `log(1 + daily count)`. Amber marks active days. The orbiting point is decorative; it does not represent a live feed.
- **Terrain:** exactly 365 consecutive days ending at the last observed date. Columns are Monday-based weeks, rows are weekdays. Height uses `log(1 + daily count)`, normalized to the peak count. Empty tiles are genuine zero days; amber roofs mark peak days. The moving survey line is decorative.
- **Signal:** the most recent eight Monday-based weeks. Wick = minimum and maximum daily contributions; candle body = first and last observed day's count. Filled amber means the last count is at least the first; outlined gray means it decreased. Flat lines can be inactive weeks or equal first/last counts. Lower bars show weekly totals. The last week may be partial.
- **Totals:** the seven- and thirty-day windows end at the last observed date, not the viewer's current local date. The snapshot time appears in the footer.

These are contributions as reported by GitHub's public calendar, which can include commits, pull requests, issues and reviews. They are not a commit-only counter, a financial series, a productivity score, or a claim that every project was authored from scratch. No private repository names or details are requested or exposed. GitHub may include anonymous private counts if the profile owner has enabled that option.

## Updating the profile

The workflow runs daily at 06:17 UTC, when the relevant source files change, or manually from **Actions → Update profile observatory → Run workflow**. Scheduled runs can be delayed by GitHub.

The public HTML calendar is fetched directly from GitHub without a personal token. The parser validates dates, counts and continuity before replacing the previous snapshot. A missing tooltip, changed markup or a failed request stops the update; the last valid SVGs remain displayed with their original timestamp.

Python 3.11 or later is sufficient; these scripts use only the standard library:

```sh
python -m unittest discover -s tests -v
python scripts/fetch_contributions.py
python scripts/render_observatory.py
```

For an offline render, skip fetching and use the committed snapshot. Do not edit `README.md` or the generated SVGs directly: change `data/observatory.json` for profile text, stack and project selection, then rerun the renderer. Update the palettes in `scripts/render_observatory.py` to change colors.

The README uses themed `<picture>` elements. Each selected project is a separate image wrapped in a real HTML link, so its destination works on GitHub without embedding interactive links in SVG. Each SVG is self-contained, has title/description text and has a legible static state. CSS motion is subtle and disabled for `prefers-reduced-motion`.

The previous terminal assets and scripts remain in the repository as an archive. They are no longer referenced by the profile or daily workflow.

## Project attribution

The profile links to actual public repositories and retains their lineage:

- Mint builds on Universal x86 Tuning Utility; see the project's license and credits.
- ValthvnQuota is a fork of CodexQuota, extended with Antigravity support; see its README.
- Antigravity RPC is a process watcher for Discord Rich Presence.

The observatory generator and its SVGs were built specifically for this profile. The conceptual inspiration is contribution-driven art such as [GitHub Gravity](https://github.com/flycran/github-gravity), [GitHub Profile 3D Contrib](https://github.com/yoshi389111/github-profile-3d-contrib), [Snake and Commits](https://github.com/dahan8473/snake-and-commits) and [GitHub Candles](https://github.com/starlash7/github-candles). Their code and assets are not included.
