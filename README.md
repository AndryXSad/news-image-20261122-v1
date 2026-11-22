# The Daily Globe — 22 November 2026

[![news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/AndryXSad/news-image-20261122-v1/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/AndryXSad/news-image-20261122-v1/reward.svg)](https://make.fun/bounty/news-image-20261122)

One front page that sums up Sunday 22 November 2026 in a single image:
45 verified stories — three leads (COP31 nearing a deal in Antalya after
three days of overtime with fossil fuels still unnamed, Russia's overnight
drone attack on Ukraine, and Iran's strikes at US bases in Bahrain), a
world map with eight places, a UTC timeline of five moments, a
day-in-figures strip, one top story from each of seven regions, a
twenty-four-item grid with no repeated dateline, and an "Also today"
ticker. Every story was checked against reporting dated 22 November 2026
before it was drawn; see `STORIES.md` in the build directory for the
story list, sources, and the stories deliberately left out.

This is a fresh build for the 22 November edition, written from a design
description (not copied from the 20 or 21 November entries). Lessons
carried over from the earlier editions: all 24 grid datelines are unique,
the footer credits only outlets actually cited, every map pin is verified
on land by a point-in-polygon check, the lead illustrations are drawn on
their own layers so nothing can escape its frame, and the program falls
back to the pre-rendered `entry.png` when PIL is unavailable. Date traps
were checked one by one: the 400-drone barrage on Ukraine, the
EU–Indonesia deal, the Geneva "killer robots" talks, the Sparta II fire,
the Basra power-station fire, the "El Chapo Isidro" capture, the Maluku
and Peru quakes, the Nitish Setu inauguration, the Norway oil ruling and
the Nvidia CEO resignation are all 12–21 November, not the 22nd, and
were left out as stories of their own.

## How it is made

`main.py` renders the page from scratch with PIL (DejaVu fonts) into
`entry.png` — 1024×1024, deterministic: the same run always produces
the same bytes. When the grader sets `MAKEFUN_OUTPUT_DIR`, the image
is written there and nowhere else. If PIL is unavailable, `main.py`
falls back to copying the pre-rendered `entry.png` shipped in this
repository.

## Run it

```sh
python3 main.py                                # renders entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py         # renders entry.png into out/
```

## License

MIT — see `LICENSE`.
