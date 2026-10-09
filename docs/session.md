# Session 005

The profile is a monochrome shell narrative: a connection command is typed, the existing ASCII portrait appears, `whoami` prints the supplied profile information, and the prompt hands navigation to actual README links and expandable sections.

The visual direction follows the shared conversation about a README as an interface, with inspiration from [Andrew6rant's self-contained profile SVGs](https://github.com/Andrew6rant/Andrew6rant) and [RyMe.md's animated banner approach](https://github.com/ryanpolasky/ryme.md). No reference code or assets were copied. This version reuses this repository's portrait, SVG helpers, project list and validated contribution parser.

The SVG uses a short one-shot CSS typing sequence, gradual portrait reveal and blinking cursor. Reduced-motion preferences disable all animations and display the complete output immediately. Animations play automatically; they do not execute shell commands. HTML repository links and native `details` sections provide the actual interaction. There is no JavaScript or embedded external service.

The activity trace contains exactly 90 chronological observed days. Every column retains its date and contribution count; heights are linear relative to the largest day in the displayed window. Dim two-pixel marks represent zero, not one contribution. The 365-day total is independently summed over the validated full calendar. The snapshot date remains visible if a refresh fails.

```sh
python scripts/render_session.py
python -m unittest discover -s tests -q
```

The daily workflow fetches the public calendar with the existing fetcher, regenerates this edition, tests it and commits changes. Prior editions and their snapshot branches are preserved. Text in the illustration scales with the image on narrow screens; the toolbox and help remain selectable Markdown.
