# Profile editions

Each tested design has a complete snapshot branch, including its README, SVGs, data, sources, scripts and refresh workflow. The default branch `main` contains the version currently displayed on the profile.

| Version | Design | Complete snapshot | Status |
| --- | --- | --- | --- |
| v1 | Activity observatory — charcoal, amber, radial fingerprint, architectural terrain and weekly candles | [v1](https://github.com/valthvn/valthvn/tree/v1) | Saved |
| v2 | Édition — paper, ink and cobalt, halftone avatar, real application captures and editorial project pages | [v2](https://github.com/valthvn/valthvn/tree/v2) | Saved |
| v3 | Holo EX — Pokémon-inspired full-art card with actual perspective motion, iridescent foil and glow | [v3](https://github.com/valthvn/valthvn/tree/v3) | Displayed on main |

The v1 snapshot is commit `e47075b327d4f7d890027b3ea093cb7fffcb2bff`.

Snapshot branches are deliberately not advanced by daily refreshes. The active design's contribution data can keep updating on `main` without changing the recorded visual version.

## Selecting a version

To select a previous design, restore that branch's complete tree as a new commit on `main`. Restore the renderer, its inputs and its workflow together with the README and artwork, so the next scheduled refresh retains the chosen design. Do not force-reset history or restore only the README.

After switching, update the displayed-version status in this table while retaining all saved snapshot branches. New experiments receive successive `v4`, `v5`, etc. names.
