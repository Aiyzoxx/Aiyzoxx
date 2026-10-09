# Session 005

The profile is a monochrome shell narrative: a connection command is typed, the existing ASCII portrait appears, `whoami` prints the supplied profile information, and the prompt hands navigation to actual README links and expandable sections.

The visual direction follows the shared conversation about a README as an interface, with inspiration from [Andrew6rant's self-contained profile SVGs](https://github.com/Andrew6rant/Andrew6rant) and [RyMe.md's animated banner approach](https://github.com/ryanpolasky/ryme.md). No reference code or assets were copied. This version reuses this repository's portrait, SVG helpers, project list and validated contribution parser.

The SVG uses a one-shot typing sequence. Following [Avi Vashishta's portrait animation](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29), a cursor sweeps each portrait row from left to right, then advances to the next row; printing takes 5.8 seconds and the completed portrait holds. Explicit glyph coordinates retain the whitespace-alignment correction. Reduced-motion preferences disable animation, reveal every row and hide the scanning cursor. Animations do not execute shell commands. HTML repository links and native `details` sections provide the actual interaction; there is no JavaScript or external image service.

The activity panel follows the trading layout of [github-candles](https://github.com/starlash7/github-candles), in monochrome: 90 daily candles, an OHLC readout, right axis, last-value marker and daily volume bars. Each candle opens at the previous trailing seven-day contribution total and closes at the current trailing seven-day total. High and low equal the larger and smaller endpoints; no intraday activity is invented. Rising candles are filled white, falling candles are hollow and flat candles are horizontal lines. Volume is the actual daily count; zero days have no volume bar. The 365-day and 90-day totals are independently summed over the validated calendar, with the snapshot date visible. These are GitHub contributions, not exclusively commits or financial prices.

```sh
python scripts/render_session.py
python -m unittest discover -s tests -q
```

The daily workflow fetches the public calendar with the existing fetcher, regenerates this edition, tests it and commits changes. Prior editions and their snapshot branches are preserved. Text in the illustration scales with the image on narrow screens; the toolbox and help remain selectable Markdown.
