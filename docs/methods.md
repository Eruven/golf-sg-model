---
title: "Scratch-Calibrated Strokes Gained"
subtitle: "A course-specific baseline for measuring an amateur's game against a scratch golfer"
author: "David Xie"
date: "October 2026"
geometry: margin=1in
fontsize: 11pt
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - \usepackage{amsmath}
  - \usepackage{booktabs}
---

# Why a different baseline

Strokes gained measures how many strokes a shot saved relative to a baseline golfer: a shot's value is the expected strokes to hole out from where it started, minus the expected strokes from where it finished, minus one. The framework is Mark Broadie's and it is the right way to decompose a score. The question is who the baseline golfer is and what course they are playing.

For a player trying to reach scratch, the natural baseline is a scratch golfer, and the natural course is the one being played. Standard strokes-gained tables are course-blind: a 356-yard par 4 with out of bounds on both sides of a 45-yard corridor is scored like a 356-yard par 4 with open rough, so the layup a good player would choose on the first is marked as a poor tee shot. The tables are also built from a single population, which fixes what "zero" means; the gap between a scratch golfer and the PGA Tour is three to four strokes a round and sits mostly in approach play, so the choice of population changes which part of a game looks weak.

This note builds the baseline for a **scratch golfer on a specific course**. The expected-strokes tables come from published scratch statistics (Shot Scope, Arccos). Tee shots on par 4s and 5s come from a decision model that knows the corridor width and where the trouble is. Hole expectations are then calibrated so the eighteen holes sum to the USGA course rating, converted from a good-day score to an average one. Worked example: Fox Creek Golf Club, Smyrna GA, Green tees, 3,802 yards, par 62, rating 59.9.

Notation: $E(\text{lie}, d)$ is the expected number of strokes for the baseline golfer to hole out. Distances are in yards except on the green, where $d$ is in feet.

# 1. Strokes gained

$$\text{SG} = E(\text{start}) - E(\text{end}) - 1 - \text{penalty}$$

# 2. Putting

From the scratch one-putt rate $p_1$, three-putt rate $p_3$ and four-putt rate $p_4$ at each anchor distance,

$$E_G(f) = 2 - p_1 + p_3 + p_4$$

The exact value is $2 - p_1 + p_3 + 2p_4$; the simplification is conservative by $p_4$, under 0.04 at any distance. Anchors are interpolated linearly; distances are rounded to the nearest foot.

| Feet | $p_1$ | $p_3$ | $E_G$ |
|:----:|:-----:|:-----:|:-----:|
| 3 | 0.94 | 0.000 | 1.06 |
| 5 | 0.73 | 0.002 | 1.27 |
| 10 | 0.36 | 0.012 | 1.65 |
| 15 | 0.22 | 0.030 | 1.81 |
| 20 | 0.14 | 0.055 | 1.92 |
| 30 | 0.065 | 0.13 | 2.07 |
| 40 | 0.035 | 0.20 | 2.17 |
| 60 | 0.018 | 0.34 | 2.34 |

Published inputs: Shot Scope 0-handicap make rates by band (two tables, which disagree at 12–18 ft; the midpoint is used); Arccos three-putt rates for 1–5 index players (9.4% from 20–25 ft, 19.6% from 25+ ft); an Arccos scratch figure of about 25% from 36–40 ft; Shot Scope scratch figures of 3% three-putts per hole and 4.6 ft left after a first putt from 30 ft.

# 3. Approach shots, 50–250 yards

Condition on hitting the green. With $g$ the GIR probability, $x$ the mean on-green proximity and $E_{\text{miss}}$ the short-game value of a typical miss,

$$E_F(d) = 1 + g(d)\,E_G\big(\kappa\,x(d)\big) + \big(1 - g(d)\big)\,E_{\text{miss}}(d)$$

The factor $\kappa = 0.7$ corrects for the spread of proximity around its mean. $E_G$ is concave, so by Jensen's inequality $\mathbb{E}[E_G(X)] < E_G(\mathbb{E}[X])$; using $0.7\,\bar x$ reproduces published tour fairway values from tour GIR and proximity to within about 0.05.

Shot Scope publishes proximity *including* misses, $\bar x$, by distance band. With $m$ the mean miss distance,

$$\bar x = g\,x + (1-g)\,m$$

The anchors for $g$ and $x$ were chosen so this holds with plausible miss distances (53, 59, 70 and 111 ft for the four bands) and an overall GIR near the published 52–59%. At 125 yards: $0.62 \times 25 + 0.38 \times 59 = 38$ ft, matching the published 38 ft for 100–150 yards, and

$$E_F(125) = 1 + 0.62\,E_G(17.5) + 0.38\,(2.55) = 1 + 0.62\,(1.87) + 0.97 \approx 3.13$$

| Yards | GIR | On-green proximity (ft) | $E_{\text{miss}}$ | $E_F$ |
|:-----:|:---:|:-----------------------:|:-----------------:|:-----:|
| 50 | 0.80 | 14 | 2.45 | 2.80 |
| 100 | 0.68 | 21 | 2.50 | 3.03 |
| 150 | 0.55 | 30 | 2.60 | 3.23 |
| 200 | 0.38 | 42 | 2.72 | 3.47 |
| 250 | 0.22 | 55 | 2.90 | 3.64 |

Rough and fairway-bunker lies use the same formula with scaled inputs: $g \times 0.8$, $x \times 1.25$, $E_{\text{miss}} + 0.10$ for rough; $0.65$, $1.30$, $+0.20$ for sand. From 150 to 250 yards the value is the better of going for the green and laying up, where

$$E_{\text{layup}}(d) = 1 + 0.7\,E_F(L) + 0.3\,E_R(L), \qquad L = \max(d - 220,\ 30)$$

Beyond 250 yards only the layup branch applies.

# 4. Around the green and recovery

Inside 50 yards, an up-and-down is two strokes and a failure is usually three. With $u$ the up-and-down rate and $\varepsilon \approx 0.03$ for double chips and three-putts net of holed shots,

$$E_{\text{ARG}} \approx 2u + 3(1-u) + \varepsilon = 3 - u + \varepsilon$$

Scratch inputs: 63% inside 25 yards, 32% from 25–50 yards, 37% sand saves. Chips from rough add 0.20.

A recovery shot (blocked by trees) is a punch-out that gains about 100 yards into a fairway/rough mix, with $d' = \max(d - 100, 15)$:

$$E_X(d) = 1.10 + 0.6\,E_F(d') + 0.4\,E_R(d')$$

# 5. Tee shots on par 4s and 5s

For a club with distance $D$ and lateral standard deviation $\sigma = sD$, on a corridor of width $w$, a normal miss distribution gives the probability of staying in play

$$P_{\text{in}} = 2\,\Phi\!\left(\frac{w/2}{\sigma}\right) - 1$$

Misses split evenly left and right. A tree-side miss becomes a recovery lie. An out-of-bounds miss is stroke and distance, which means replaying from the tee at the same expectation $E$; solving the recursion,

$$E = 1 + P_{\text{in}}E_{\text{in}} + P_{\text{tree}}E_X + P_{\text{OB}}(1 + E)
\quad\Longrightarrow\quad
E = \frac{1 + P_{\text{in}}E_{\text{in}} + P_{\text{tree}}E_X + P_{\text{OB}}}{1 - P_{\text{OB}}}$$

with $E_{\text{in}} = 0.7\,E_F(L) + 0.3\,E_R(L)$ and $L = \max(\text{hole length} - D, 15)$. The hole's value is the minimum over the scratch club set, i.e. a scratch golfer picks the right club. Par 3s use $E_F$ at the hole's yardage from the tee.

| Club | Distance (yds) | $\sigma$ (% of distance) | Basis |
|:-----|:--------------:|:------------------------:|:------|
| Driver | 262 | 7.5 | Shot Scope P-avg 285 $\times$ 0.92; Arccos big-miss rate implies $\sigma \approx 20$–22 yds |
| 3-wood | 245 | 8.0 | Shot Scope P-avg 261–267 $\times$ 0.92; fairway % barely better than driver |
| 3-hybrid | 203 | 7.5 | Shot Scope scratch average 197, P-avg 219; dispersion assumed |
| 5-iron | 185 | 7.0 | Shot Scope P-avg 200 $\times$ 0.92; dispersion assumed |

| Hole | Yards | Trouble | Scratch best club | Raw $E$ |
|:----:|:-----:|:--------|:-----------------:|:-------:|
| 1 | 356 | OB both sides | 5-iron | 4.55 |
| 3 | 262 | OB right | 3-wood | 3.89 |
| 6 | 397 | Trees | Driver | 4.37 |
| 9 | 301 | Trees | Driver | 3.95 |
| 11 | 333 | Trees | Driver | 4.10 |
| 14 | 260 | Trees | 3-wood | 3.72 |
| 16 | 321 | OB right | Driver | 4.30 |

# 6. Calibration to the course rating

The raw hole values sum to 64.15 at Fox Creek. The course rating, 59.9, is a scratch golfer's *good* day, not an average one: a Handicap Index is built from the best 8 of 20 differentials, and the expected mean of the best 8 of 20 normal draws sits $0.93\sigma$ below the mean. With a scratch golfer's round-to-round standard deviation of about 2.6 strokes, an average scratch round is

$$\text{target} = \text{CR} + 0.93 \times 2.6 \approx \text{CR} + 2.4 = 62.3$$

which is the population the Shot Scope and Arccos tables describe. The remaining gap, $62.3 - 64.15 = -1.85$, is the course itself playing easier than its yardages for a scratch golfer, and it is spread over holes with weights that sum to one for any $\lambda$ (171 is the sum of 1 to 18):

$$a_h = \Big(\text{target} - \textstyle\sum_h E_h^{\text{raw}}\Big)\,\omega_h,
\qquad
\omega_h = \frac{1-\lambda}{18} + \lambda\,\frac{19 - \text{SI}_h}{171}$$

With $\lambda = 0$ every hole gets $a_h = -0.10$. A negative adjustment means the course plays easier than a generic course with the same hole lengths once tightness is already in the tee model; at Fox Creek that is mostly the short, wedge-length par 3s.

Within a hole, each position gets an adjusted expectation $E' = E + a_h\,w$ with

$$w = \begin{cases} 1 & \text{tee} \\ 0 & \text{on the green} \\ \operatorname{clip}\!\left[\dfrac{E - g_0}{E_{\text{tee}} - g_0},\ 0,\ 1\right] & \text{otherwise} \end{cases}, \qquad g_0 = 1.85$$

Summing SG over a hole telescopes to $E_h^{\text{raw}} + a_h - \text{strokes}$ regardless of $w$, so over eighteen holes total SG is exactly $\text{target} - \text{score} = \text{CR} + 2.4 - \text{score}$. Because $w = 0$ on the green, putting strokes gained never carries a course adjustment: zero in the putting column means putting like the published scratch data.

# 7. Worked example: hole 1, driver to 102 yards in the fairway

| Shot | $E'(\text{start})$ | $E'(\text{end})$ | SG |
|:-----|:------------------:|:----------------:|:--:|
| Drive, tee to fairway at 102 yds | $4.55 - 0.10 = 4.45$ | $3.03 - 0.10 \times 0.44 = 2.99$ | $+0.46$ |
| Wedge, 102 yds to 22 ft | 2.99 | $E_G(22) = 1.95$ | $+0.04$ |
| First putt, 22 ft to 3 ft | 1.95 | 1.06 | $-0.11$ |
| Second putt, holed | 1.06 | 0 | $+0.06$ |

The drive beats the scratch baseline, a 5-iron layup, by about half a stroke. The weight on the 102-yard position is $w = (3.03 - 1.85)/(4.55 - 1.85) = 0.44$; the putts carry no adjustment.

# 8. What is data and what is assumption

| Component | Source | Status |
|:----------|:-------|:-------|
| Putting make and three-putt rates by distance | Shot Scope (0 hcp), Arccos | Published |
| Approach proximity incl. misses by band; overall GIR | Shot Scope | Published |
| Split of each band into GIR and on-green proximity | Fitted to the published band averages | Derived |
| Up-and-down inside 25 and 25–50 yds; sand save | Shot Scope | Published |
| Scratch club distances | Shot Scope P-avg $\times$ 0.92 | Derived |
| Driver and 3-wood dispersion | Arccos big-miss rate; Shot Scope fairway % | Derived |
| Hybrid and long-iron dispersion; rough and bunker factors; recovery and layup rules; $\kappa$ | — | Assumption |

Scratch sits behind tour by roughly $+0.02$ to $+0.13$ strokes on putts, $+0.05$ to $+0.15$ around the green and $+0.2$ to $+0.3$ on approaches, consistent with Broadie's finding that approach play is the largest scratch-to-tour gap. The planned extension is credibility weighting: after $n$ logged rounds, blend the model's hole values with observed hole averages using a Bühlmann-style weight $Z = n/(n+k)$, so assumed parameters give way to measured ones as data accumulates.

Code, tests and the spreadsheet: [github.com/Eruven/golf-sg-model](https://github.com/Eruven/golf-sg-model).

# Sources

- Putting make percentage by handicap, fine bands. MyGolfSpy / Shot Scope. <https://mygolfspy.com/news-opinion/putting-make-percentage-by-handicap-full-chart-are-you-above-or-below-average/>
- Putting make percentages by handicap. Shot Scope. <https://shotscope.com/blog/practice-green/stats-and-data/putting-make-percentages-by-handicap-how-do-you-compare/>
- Three-putting stats by handicap. MyGolfSpy / Shot Scope. <https://mygolfspy.com/news-opinion/shot-scope-case-study/>
- Three-putt likelihood by handicap and distance. Golf.com, Lou Stagner / Arccos. <https://golf.com/instruction/putting/how-likely-to-three-putt-play-smart/>
- Pros vs Joes: analyzing 3-putts. Arccos. <https://eu.arccosgolf.com/blogs/community/pros-vs-joes-analyzing-3-putts>
- Scratch vs 10 vs 20 handicap stats. Golf Monthly / Shot Scope. <https://www.golfmonthly.com/features/scratch-vs-10-vs-20-handicap-how-the-stats-compare>
- Approach proximity by distance band. Golf Monthly / Shot Scope. <https://www.golfmonthly.com/features/how-close-to-the-pin-do-amateur-golfers-hit-their-approach-shots>
- GIR by handicap. Golf Monthly / Shot Scope. <https://www.golfmonthly.com/features/how-many-greens-in-regulation-does-an-average-golfer-hit>
- Short game performance by handicap. MyGolfSpy / Shot Scope. <https://mygolfspy.com/news-opinion/instruction/how-good-is-your-short-game-performance-chart-by-handicap/>
- Driver vs 3-wood accuracy by handicap. MyGolfSpy / Shot Scope. <https://mygolfspy.com/news-opinion/driver-versus-3-wood-accuracy-comparison-which-finds-more-fairways/>
- Big miss with driver by handicap. Lou Stagner / Arccos. <https://newsletter.loustagnergolf.com/p/big-miss-with-driver>
- PGA Tour make and three-putt rates by distance. Golfing Focus / Broadie. <https://golfingfocus.com/what-percentage-of-putts-do-pros-make-tv-does-not-tell-the-story/>
- Fox Creek Golf Club scorecard and rating. Golfify. <https://www.golfify.io/courses/fox-creek-golf-club-smyrna>
- Mark Broadie, *Every Shot Counts*, Gotham Books, 2014.
