# Methods

Notation: $E(\text{lie}, d)$ is the expected number of strokes for the baseline golfer to hole out from a position. Yards everywhere except on the green, where $d$ is in feet.

## 1. Strokes gained

$$\text{SG} = E(\text{start}) - E(\text{end}) - 1 - \text{penalty}$$

## 2. Putting

From the scratch one-putt rate $p_1$, three-putt rate $p_3$ and four-putt rate $p_4$ at each anchor distance,

$$E_G(f) = 2 - p_1 + p_3 + p_4$$

(exact value is $2 - p_1 + p_3 + 2p_4$; the simplification is conservative by $p_4$, under 0.04 at any distance). Anchors are interpolated linearly; distances are rounded to the nearest foot and clipped to 1–100.

Published inputs: Shot Scope 0-handicap make rates by band (two tables, which disagree at 12–18 ft; the midpoint is used), Arccos three-putt rates for 1–5 index players (9.4% from 20–25 ft, 19.6% from 25+ ft), an Arccos scratch figure of about 25% from 36–40 ft, and Shot Scope's scratch figures of 3% three-putts per hole and 4.6 ft left after a first putt from 30 ft.

## 3. Approach shots, 50–250 yards

Condition on hitting the green, with $g$ the GIR probability, $x$ the mean on-green proximity and $E_{\text{miss}}$ the short-game value of a typical miss:

$$E_F(d) = 1 + g(d)\,E_G\big(\kappa\,x(d)\big) + \big(1 - g(d)\big)\,E_{\text{miss}}(d)$$

$\kappa = 0.7$ corrects for the spread of proximity around its mean. $E_G$ is concave, so by Jensen's inequality $\mathbb{E}[E_G(X)] < E_G(\mathbb{E}[X])$; using $0.7\,\bar x$ reproduces published tour fairway values from tour GIR and proximity to within about 0.05.

Shot Scope publishes proximity *including* misses, $\bar x$, by band. With $m$ the mean miss distance,

$$\bar x = g\,x + (1-g)\,m$$

The anchors for $g$ and $x$ were chosen so this holds with plausible $m$ (53, 59, 70 and 111 ft for the four bands) and an overall GIR near the published 52–59%. The split itself is therefore derived, not published.

Rough and fairway-bunker lies use the same formula with scaled inputs ($g \times 0.8$, $x \times 1.25$, $E_{\text{miss}} + 0.10$ for rough; $0.65$, $1.30$, $+0.20$ for sand). From 150 to 250 yards the value is $\min(\text{approach}, \text{layup})$ where

$$E_{\text{layup}}(d) = 1 + 0.7\,E_F(L) + 0.3\,E_R(L), \qquad L = \max(d - 220, 30)$$

Beyond 250 yards only the layup branch applies.

## 4. Around the green and recovery

With $u$ the up-and-down rate and $\varepsilon \approx 0.03$ for double chips and three-putts net of holed shots,

$$E_{\text{ARG}} \approx 2u + 3(1-u) + \varepsilon = 3 - u + \varepsilon$$

Scratch inputs: 63% inside 25 yards, 32% from 25–50, 37% sand saves. Chips from rough add 0.20.

A recovery shot gains about 100 yards into a fairway/rough mix, with $d' = \max(d - 100, 15)$:

$$E_X(d) = 1.10 + 0.6\,E_F(d') + 0.4\,E_R(d')$$

## 5. Tee shots on par 4s and 5s

For a club with distance $D$ and lateral $\sigma = s D$ on a corridor of width $w$, under a normal miss,

$$P_{\text{in}} = 2\Phi\!\left(\frac{w/2}{\sigma}\right) - 1$$

Misses split evenly left and right; a tree-side miss is a recovery lie and an OB miss is stroke and distance, i.e. a replay from the tee at the same expectation. Solving the recursion

$$E = 1 + P_{\text{in}}E_{\text{in}} + P_{\text{tree}}E_X + P_{\text{OB}}(1 + E)
\;\Rightarrow\;
E = \frac{1 + P_{\text{in}}E_{\text{in}} + P_{\text{tree}}E_X + P_{\text{OB}}}{1 - P_{\text{OB}}}$$

with $E_{\text{in}} = 0.7\,E_F(L) + 0.3\,E_R(L)$ and $L = \max(\text{hole} - D, 15)$. The hole's expectation is the minimum over the scratch club set, i.e. a scratch golfer picks the right club. Par 3s use $E_F(\text{yards})$ from the tee.

## 6. Calibration to the course rating

Let $E_h^{\text{raw}}$ be the hole expectations and $\text{CR}$ the course rating (optionally plus a good-day gap). The residual is spread with weights that sum to one for any $\lambda$:

$$a_h = \Big(\text{CR} - \textstyle\sum_h E_h^{\text{raw}}\Big)\,\omega_h,
\qquad
\omega_h = \frac{1-\lambda}{18} + \lambda\,\frac{19 - \text{SI}_h}{171}$$

Within a hole, each position gets $E' = E + a_h\,w$ with

$$w = \begin{cases} 1 & \text{tee} \\ 0 & \text{on the green} \\ \operatorname{clip}\!\left[\dfrac{E - g_0}{E_{\text{tee}} - g_0},\,0,\,1\right] & \text{otherwise} \end{cases}, \qquad g_0 = 1.85$$

Summing SG over a hole telescopes to $E_h^{\text{raw}} + a_h - \text{strokes}$ regardless of $w$, so over 18 holes total SG is exactly $\text{CR} - \text{score}$. Because $w = 0$ on the green, putting strokes gained never carries course adjustment.

## 7. Limitations and next steps

- Per-club dispersion for hybrids and long irons, the rough and bunker factors, and the recovery and layup rules are assumptions.
- Course ratings on short executive courses can be generous; a generous rating shows up as a negative course adjustment.
- The planned extension is credibility weighting: after $n$ logged rounds, blend the baseline hole values with observed hole averages using a Bühlmann-style weight $Z = n/(n+k)$, so the model moves from assumed parameters toward measured ones as data accumulates.
