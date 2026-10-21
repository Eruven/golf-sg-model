# golfsg — scratch-calibrated, course-specific strokes gained

Strokes gained tells you how many strokes a shot saved relative to a baseline golfer. Every app computes it against a baseline that is the same on every course. This model builds the baseline for **a scratch golfer on a specific course**:

1. **Expected-strokes tables for a scratch golfer** are derived from published scratch statistics (Shot Scope, Arccos): make and three-putt rates by distance, GIR and proximity by approach distance, up-and-down and sand-save rates.
2. **Tee shots on par 4s and 5s** come from a decision model: for each club, a normal lateral miss against the corridor width, with trees as a recovery lie and out of bounds as stroke and distance. The hole's value is the best club's expectation.
3. **Hole expectations are calibrated to the USGA course rating**, so the 18 holes sum to what a scratch golfer is rated to shoot there. The adjustment is applied only to shots that start off the green, so putting is always measured straight against the scratch putting data.

Over a full round, total strokes gained equals `course rating − score` exactly; the model's job is to split that total into off-the-tee, approach, around-the-green and putting in a way that is anchored to data rather than guessed.

Full derivation: [docs/methods.md](docs/methods.md).

## Install

```bash
pip install -e ".[dev]"
pytest
```

No runtime dependencies. `openpyxl` is only needed for `scripts/build_workbook.py`.

## Use

```bash
# Show the calibrated course and the scratch club choice on each hole
python -m golfsg.cli data/fox_creek.json --tour-check

# Score a shot log (hole, start_lie, start_dist, end_lie, end_dist, penalty)
python -m golfsg.cli data/fox_creek.json --shots data/example_round.csv
```

```python
from golfsg import Baseline, Course, Shot, calibrate, score_round

base = Baseline()                                   # scratch tables from published data
cal = calibrate(Course.from_json("data/fox_creek.json"), base)
cal.by_number(1).best_club                          # '5-iron' (OB both sides, 45-yd corridor)
res = score_round([Shot(1, "T", 356, "F", 102), Shot(1, "F", 102, "G", 22),
                   Shot(1, "G", 22, "G", 3), Shot(1, "G", 3, "H")], base, cal)
res["by_category"]                                  # {'OTT': 0.38, 'APP': -0.02, 'ARG': 0, 'PUTT': -0.05}
```

Lies: `T` tee, `F` fairway/fringe, `R` rough, `S` sand, `X` recovery (blocked), `G` green (distance in **feet**), `H` holed.

## Adding a course

Copy `data/fox_creek.json`: scorecard yardages, stroke index, course rating for the tees played, and for each par 4/5 the corridor width and trouble type (`X` trees both sides, `OB` both sides, `OBR`/`OBL` one side).

## What is data, what is assumption

| Component | Source | Status |
| --- | --- | --- |
| Putting make / three-putt rates by distance | Shot Scope (0 hcp), Arccos (Stagner) | Published |
| Approach proximity incl. misses by band, overall GIR | Shot Scope | Published |
| Split of each band into GIR and on-green proximity | Fitted to reproduce the published band averages | Derived |
| Up-and-down <25 / 25–50 yds, sand save | Shot Scope | Published |
| Scratch club distances | Shot Scope P-avg × 0.92 | Derived |
| Driver / 3-wood dispersion | Arccos big-miss rate; Shot Scope fairway % | Derived |
| Hybrid / long-iron dispersion, rough and bunker factors, recovery, layup rules, Jensen factor | — | Assumption |

All assumptions live in `golfsg/params.py` with their basis stated. The intended next step is to replace them with credibility-weighted estimates from logged rounds.

## Sanity checks

- Scratch sits behind tour by +0.02–0.13 on putts, +0.05–0.15 around the green and +0.2–0.3 on approaches (Broadie: approach play is the largest scratch-to-tour gap). `--tour-check` prints the comparison.
- A scratch golfer's good-day score at Fox Creek is reproduced by construction (59.9); the raw model's average-scratch total is 64.2, about 2.5 of which is the good-day gap.
- `tests/` cover the putting identity, table monotonicity, the OB fixed point, calibration weights, telescoping of SG within a hole, and agreement with the Excel workbook.

## Workbook

`data/Fox_Creek_Scratch_SG.xlsx` is the same model with live formulas (shot log, per-round category totals, editable inputs). `scripts/build_workbook.py` regenerates it.

## Sources

- [Putting make percentage by handicap — MyGolfSpy / Shot Scope](https://mygolfspy.com/news-opinion/putting-make-percentage-by-handicap-full-chart-are-you-above-or-below-average/)
- [Putting make percentages by handicap — Shot Scope](https://shotscope.com/blog/practice-green/stats-and-data/putting-make-percentages-by-handicap-how-do-you-compare/)
- [Three-putting stats by handicap — MyGolfSpy / Shot Scope](https://mygolfspy.com/news-opinion/shot-scope-case-study/)
- [Three-putt likelihood by handicap and distance — Golf.com / Lou Stagner, Arccos](https://golf.com/instruction/putting/how-likely-to-three-putt-play-smart/)
- [Pros vs Joes: analyzing 3-putts — Arccos](https://eu.arccosgolf.com/blogs/community/pros-vs-joes-analyzing-3-putts)
- [Scratch vs 10 vs 20 handicap stats — Golf Monthly / Shot Scope](https://www.golfmonthly.com/features/scratch-vs-10-vs-20-handicap-how-the-stats-compare)
- [Approach proximity by distance band — Golf Monthly / Shot Scope](https://www.golfmonthly.com/features/how-close-to-the-pin-do-amateur-golfers-hit-their-approach-shots)
- [GIR by handicap — Golf Monthly / Shot Scope](https://www.golfmonthly.com/features/how-many-greens-in-regulation-does-an-average-golfer-hit)
- [Short game performance by handicap — MyGolfSpy / Shot Scope](https://mygolfspy.com/news-opinion/instruction/how-good-is-your-short-game-performance-chart-by-handicap/)
- [Driver vs 3-wood accuracy by handicap — MyGolfSpy / Shot Scope](https://mygolfspy.com/news-opinion/driver-versus-3-wood-accuracy-comparison-which-finds-more-fairways/)
- [Big miss with driver by handicap — Lou Stagner, Arccos](https://newsletter.loustagnergolf.com/p/big-miss-with-driver)
- [PGA Tour make and three-putt rates by distance — Golfing Focus / Broadie](https://golfingfocus.com/what-percentage-of-putts-do-pros-make-tv-does-not-tell-the-story/)
- [Fox Creek Golf Club scorecard and rating — Golfify](https://www.golfify.io/courses/fox-creek-golf-club-smyrna)
- Mark Broadie, *Every Shot Counts* (2014) — strokes gained framework and tour reference values.
