"""3Blue1Brown-style explainer of the scratch-calibrated strokes-gained model.

Render:  manim -qh sg_explainer.py Explainer
Numbers come from golfsg (Fox Creek, Green tees, CR 59.9).
"""
from manim import *
import numpy as np
from math import erf, sqrt

# ---------- palette (3b1b-ish on dark) ----------
BG = "#0f1419"
GREEN_T = "#58c472"
RED_T = "#ff6b6b"
BLUE_T = "#5aa9ff"
GOLD_T = "#ffd166"
GREY_T = "#9aa5b1"
WHITE_T = "#f4f6f8"
config.background_color = BG

# ---------- model numbers (from golfsg) ----------
PUTT = {3: 1.06, 5: 1.27, 10: 1.65, 20: 1.92, 30: 2.07, 40: 2.17, 60: 2.34}
FAIR = {20: 2.44, 50: 2.80, 100: 3.03, 125: 3.13, 150: 3.23, 200: 3.47, 250: 3.64}
TOUR = {("G", 10): 1.61, ("G", 20): 1.87, ("G", 40): 2.06, ("F", 100): 2.80, ("F", 150): 2.95, ("F", 200): 3.19}
H1 = {"driver": (262, 19.6, 0.748, 4.73), "3-wood": (245, 19.6, 0.749, 4.79),
      "3-hybrid": (203, 15.2, 0.861, 4.63), "5-iron": (185, 13.0, 0.918, 4.55)}
RAW_TOTAL, CR, ADJ = 64.15, 59.9, -0.103


def phi(z): return 0.5 * (1 + erf(z / sqrt(2)))


def title_card(text, sub=None):
    t = Text(text, font="DejaVu Sans", weight=BOLD, color=WHITE_T).scale(0.9)
    if sub:
        s = Text(sub, font="DejaVu Sans", color=GREY_T).scale(0.45).next_to(t, DOWN, buff=0.35)
        return VGroup(t, s)
    return VGroup(t)


class Explainer(Scene):
    def construct(self):
        self.scene_title()
        self.scene_expected_strokes()
        self.scene_one_shot()
        self.scene_scratch_vs_tour()
        self.scene_tee_model()
        self.scene_compare()
        self.scene_calibration()
        self.scene_outro()

    # ---------------------------------------------------------- 0 title
    def scene_title(self):
        t = title_card("Strokes gained, against a scratch golfer",
                       "on the course you actually play")
        self.play(Write(t[0]), run_time=1.6)
        self.play(FadeIn(t[1], shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(t))

    # ---------------------------------------------------------- 1 expected strokes
    def scene_expected_strokes(self):
        h = Text("Every spot on the course has a number", font="DejaVu Sans", color=WHITE_T).scale(0.6).to_edge(UP)
        sub = Text("expected strokes to hole out, for a scratch golfer", font="DejaVu Sans", color=GREY_T).scale(0.4).next_to(h, DOWN, buff=0.15)
        self.play(FadeIn(h), FadeIn(sub))

        # a hole drawn as a line: tee (left) -> green (right)
        line = Line(LEFT * 5.8, RIGHT * 3.0, color=GREY_T, stroke_width=3).shift(DOWN * 0.6)
        green = Circle(radius=1.35, color=GREEN_T, fill_opacity=0.18).move_to(RIGHT * 4.3 + DOWN * 0.6)
        flag = VGroup(Line(ORIGIN, UP * 0.8, color=WHITE_T), Triangle(color=RED_T, fill_opacity=1).scale(0.15).rotate(-PI / 2).shift(UP * 0.68 + RIGHT * 0.12)).move_to(green.get_center() + RIGHT * 0.95 + UP * 0.35)
        self.play(Create(line), FadeIn(green), FadeIn(flag))

        # points along the hole with E values
        pts = [(-5.6, "Tee, 356 yds", "4.55", 0), (-2.4, "Fairway, 150 yds", "3.23", 0), (0.6, "Fairway, 50 yds", "2.80", 0),
               (3.4, "20 ft putt", "1.92", 0), (4.7, "3 ft putt", "1.06", 1)]
        dots, labels = VGroup(), VGroup()
        for i, (x, name, e, stag) in enumerate(pts):
            d = Dot(point=[x, -0.6, 0], color=GOLD_T, radius=0.08)
            num = Text(e, font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.55).next_to(d, UP, buff=0.25 + 0.5 * stag)
            nm = Text(name, font="DejaVu Sans", color=GREY_T).scale(0.32).next_to(d, DOWN, buff=0.25 + 0.45 * stag)
            dots.add(d); labels.add(VGroup(num, nm))
        for d, l in zip(dots, labels):
            self.play(FadeIn(d, scale=0.5), FadeIn(l, shift=UP * 0.15), run_time=0.55)
        self.wait(0.6)

        note = Text("holed = 0", font="DejaVu Sans", color=GREY_T).scale(0.4).next_to(green, DOWN, buff=0.9)
        self.play(FadeIn(note))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in [h, sub, line, green, flag, dots, labels, note]])

    # ---------------------------------------------------------- 2 one shot
    def scene_one_shot(self):
        h = Text("A shot's value is how much it moved that number", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        self.play(FadeIn(h))

        eq = MathTex(r"\text{SG} = E(\text{start}) - E(\text{end}) - 1", color=WHITE_T).scale(1.05).shift(UP * 1.2)
        self.play(Write(eq))
        self.wait(0.8)

        # Example: 102 yds fairway -> 22 ft
        start = VGroup(Text("102 yds, fairway", font="DejaVu Sans", color=GREY_T).scale(0.4),
                       Text("3.03", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.8)).arrange(DOWN, buff=0.15).shift(LEFT * 3.2 + DOWN * 0.8)
        end = VGroup(Text("22 ft, on the green", font="DejaVu Sans", color=GREY_T).scale(0.4),
                     Text("1.95", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.8)).arrange(DOWN, buff=0.15).shift(RIGHT * 3.2 + DOWN * 0.8)
        arrow = Arrow(start.get_right(), end.get_left(), color=BLUE_T, buff=0.3)
        self.play(FadeIn(start), GrowArrow(arrow), FadeIn(end))
        self.wait(0.5)

        calc = MathTex(r"3.03 - 1.95 - 1 = ", r"+0.08", color=WHITE_T).scale(0.95).shift(DOWN * 2.3)
        calc[1].set_color(GREEN_T)
        self.play(Write(calc))
        self.wait(0.8)
        tag = Text("a tiny bit better than a scratch golfer's average from there", font="DejaVu Sans", color=GREY_T).scale(0.38).next_to(calc, DOWN, buff=0.3)
        self.play(FadeIn(tag))
        self.wait(1.2)

        # bad shot variant
        self.play(FadeOut(calc), FadeOut(tag))
        end2 = VGroup(Text("45 ft, on the green", font="DejaVu Sans", color=GREY_T).scale(0.4),
                      Text("2.22", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.8)).arrange(DOWN, buff=0.15).move_to(end)
        self.play(Transform(end, end2))
        calc2 = MathTex(r"3.03 - 2.22 - 1 = ", r"-0.19", color=WHITE_T).scale(0.95).shift(DOWN * 2.3)
        calc2[1].set_color(RED_T)
        self.play(Write(calc2))
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in [h, eq, start, end, arrow, calc2]])

    # ---------------------------------------------------------- 3 scratch vs tour
    def scene_scratch_vs_tour(self):
        h = Text("The baseline: a scratch golfer, built from data", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        self.play(FadeIn(h))

        rows = [("20 ft putt", 1.87, 1.92), ("40 ft putt", 2.06, 2.17), ("100 yds, fairway", 2.80, 3.03),
                ("150 yds, fairway", 2.95, 3.23), ("200 yds, fairway", 3.19, 3.47)]
        header = VGroup(Text("", font="DejaVu Sans").scale(0.4),
                        Text("Tour", font="DejaVu Sans", weight=BOLD, color=BLUE_T).scale(0.45),
                        Text("Scratch", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.45),
                        Text("gap", font="DejaVu Sans", weight=BOLD, color=GREY_T).scale(0.45))
        table = VGroup(header)
        for name, t, s in rows:
            r = VGroup(Text(name, font="DejaVu Sans", color=GREY_T).scale(0.4),
                       Text(f"{t:.2f}", font="DejaVu Sans", color=BLUE_T).scale(0.5),
                       Text(f"{s:.2f}", font="DejaVu Sans", color=GOLD_T).scale(0.5),
                       Text(f"+{s - t:.2f}", font="DejaVu Sans", color=RED_T if s - t > 0.15 else GREY_T).scale(0.5))
            table.add(r)
        for r in table:
            for i, cell in enumerate(r):
                cell.move_to([-3.4 + i * 2.3, 0, 0])
        for i, r in enumerate(table):
            r.shift(UP * (1.6 - i * 0.62))
        self.play(FadeIn(header))
        for r in table[1:]:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait(0.8)

        brace_rows = VGroup(table[3], table[4], table[5])
        box = SurroundingRectangle(VGroup(*[r[3] for r in brace_rows]), color=RED_T, buff=0.12)
        note = Text("The gap to tour is biggest on approach shots.\nWhich baseline you measure against changes what your weakness looks like.",
                    font="DejaVu Sans", color=GREY_T, line_spacing=0.9).scale(0.36).to_edge(DOWN, buff=0.6)
        self.play(Create(box), FadeIn(note))
        self.wait(2.2)
        src = Text("scratch numbers built from Shot Scope / Arccos data on 0-handicap golfers",
                   font="DejaVu Sans", color=GREY_T).scale(0.3).next_to(note, UP, buff=0.25)
        self.play(FadeIn(src))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in [h, table, box, note, src]])

    # ---------------------------------------------------------- 4 tee model
    def scene_tee_model(self):
        h = Text("The problem: standard strokes gained doesn't know the course", font="DejaVu Sans", color=WHITE_T).scale(0.5).to_edge(UP)
        self.play(FadeIn(h))

        # Hole 1 corridor: 45 yds wide, OB both sides. Draw top-down: tee bottom, green top.
        scale = 0.075  # px per yard-ish (vertical)
        corridor_w = 45 * 0.07
        corr = Rectangle(width=corridor_w, height=5.2, color=GREEN_T, fill_opacity=0.12, stroke_width=1).shift(DOWN * 0.2 + LEFT * 2.6)
        ob_l = Rectangle(width=2.0, height=5.2, color=RED_T, fill_opacity=0.10, stroke_width=0).next_to(corr, LEFT, buff=0)
        ob_r = ob_l.copy().next_to(corr, RIGHT, buff=0)
        obl = Text("OB", font="DejaVu Sans", weight=BOLD, color=RED_T).scale(0.5).move_to(ob_l)
        obr = obl.copy().move_to(ob_r)
        tee = Dot(corr.get_bottom() + UP * 0.15, color=WHITE_T)
        label = Text("Hole 1 · 356 yds · 45 yds wide", font="DejaVu Sans", color=GREY_T).scale(0.4).next_to(corr, DOWN, buff=0.2)
        self.play(FadeIn(corr), FadeIn(ob_l), FadeIn(ob_r), FadeIn(obl), FadeIn(obr), FadeIn(tee), FadeIn(label))
        self.wait(0.5)

        # dispersion curve for driver at the landing zone
        def bell(sigma_yds, color, y):
            s = sigma_yds * 0.07
            curve = FunctionGraph(lambda x: 1.1 * np.exp(-x ** 2 / (2 * s ** 2)), x_range=[-2.2, 2.2], color=color).shift(UP * y)
            return curve

        side = VGroup()
        panel_title = Text("Scratch golfer, driver", font="DejaVu Sans", weight=BOLD, color=WHITE_T).scale(0.42)
        p1 = Text("262 yds · lateral σ ≈ 20 yds", font="DejaVu Sans", color=GREY_T).scale(0.36)
        p2 = Text("P(in play) = 2Φ(22.5/20) − 1 ≈ 75%", font="DejaVu Sans", color=GREY_T).scale(0.36)
        p3 = Text("miss = OB = stroke and distance", font="DejaVu Sans", color=RED_T).scale(0.36)
        side.add(panel_title, p1, p2, p3).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 3.4 + UP * 1.2)

        sgd = 19.6 * 0.07
        drv = FunctionGraph(lambda x: 1.1 * np.exp(-x ** 2 / (2 * sgd ** 2)), x_range=[-2.2, 2.2], color=BLUE_T).shift([corr.get_center()[0], 0.9, 0])
        self.play(FadeIn(side[0]), FadeIn(side[1]))
        self.play(Create(drv))
        # shade the tails outside the corridor
        cx = corr.get_center()[0]; sg = 19.6 * 0.07; half = corridor_w / 2
        def tail(sign):
            xs = np.linspace(half, 2.2, 25) * sign
            top = [[cx + x, 0.9 + 1.1 * np.exp(-x ** 2 / (2 * sg ** 2)), 0] for x in xs]
            base = [[cx + xs[-1], 0.9, 0], [cx + xs[0], 0.9, 0]]
            return Polygon(*(top + base), color=RED_T, fill_opacity=0.35, stroke_width=0)
        tail_l, tail_r = tail(-1), tail(1)
        self.play(FadeIn(tail_l), FadeIn(tail_r), FadeIn(side[2]), FadeIn(side[3]))
        self.wait(1.2)

        # club comparison table
        rows = [("Driver", "75%", "4.73"), ("3-wood", "75%", "4.79"), ("3-hybrid", "86%", "4.63"), ("5-iron", "92%", "4.55")]
        tbl = VGroup()
        hdr = VGroup(Text("club", font="DejaVu Sans", color=GREY_T).scale(0.34), Text("in play", font="DejaVu Sans", color=GREY_T).scale(0.34), Text("E(hole)", font="DejaVu Sans", color=GREY_T).scale(0.34))
        tbl.add(hdr)
        for n, p, e in rows:
            tbl.add(VGroup(Text(n, font="DejaVu Sans", color=WHITE_T).scale(0.38), Text(p, font="DejaVu Sans", color=GREY_T).scale(0.38), Text(e, font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.42)))
        for r in tbl:
            for i, c in enumerate(r):
                c.move_to([2.3 + i * 1.45, 0, 0])
        for i, r in enumerate(tbl):
            r.shift(DOWN * (-0.4 + i * 0.45))
        self.play(FadeOut(side), run_time=0.4)
        self.play(FadeIn(tbl[0]))
        for r in tbl[1:]:
            self.play(FadeIn(r, shift=RIGHT * 0.15), run_time=0.4)
        box = SurroundingRectangle(tbl[4], color=GREEN_T, buff=0.1)
        verdict = Text("A scratch golfer's best play here is 5-iron.\nThe hole is worth 4.55, not 4.0.", font="DejaVu Sans", color=WHITE_T, line_spacing=0.9).scale(0.38).next_to(tbl, DOWN, buff=0.35)
        self.play(Create(box), FadeIn(verdict))
        self.wait(2.0)

        punch = Text("So a smart layup scores as a smart layup,\nnot as a bad drive.", font="DejaVu Sans", color=GREEN_T, line_spacing=0.9).scale(0.4).next_to(verdict, DOWN, buff=0.35)
        self.play(FadeIn(punch))
        self.wait(2.0)
        self.play(*[FadeOut(m) for m in [h, corr, ob_l, ob_r, obl, obr, tee, label, drv, tail_l, tail_r, tbl, box, verdict, punch]])

    # ---------------------------------------------------------- 4b same shot, three scorecards
    def scene_compare(self):
        h = Text("Same shot, three ways to score it", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        sub = Text("Hole 1 · 5-iron off the tee, fairway, 171 yds left", font="DejaVu Sans", color=GREY_T).scale(0.4).next_to(h, DOWN, buff=0.15)
        self.play(FadeIn(h), FadeIn(sub))

        rows = [("Standard SG, tour baseline", "3.90", "3.03", "\u22120.13", RED_T),
                ("Scratch baseline, course-blind", "4.22", "3.32", "\u22120.10", RED_T),
                ("This model", "4.45", "3.27", "+0.18", GREEN_T)]
        hdr = VGroup(Text("", font="DejaVu Sans").scale(0.4),
                     Text("E(tee)", font="DejaVu Sans", color=GREY_T).scale(0.4),
                     Text("E(after)", font="DejaVu Sans", color=GREY_T).scale(0.4),
                     Text("SG", font="DejaVu Sans", weight=BOLD, color=GREY_T).scale(0.45))
        table = VGroup(hdr)
        for name, a, b_, sg, col in rows:
            table.add(VGroup(Text(name, font="DejaVu Sans", color=WHITE_T).scale(0.42),
                             Text(a, font="DejaVu Sans", color=GOLD_T).scale(0.5),
                             Text(b_, font="DejaVu Sans", color=GOLD_T).scale(0.5),
                             Text(sg, font="DejaVu Sans", weight=BOLD, color=col).scale(0.55)))
        xs = [-3.6, 0.6, 2.4, 4.4]
        for i, r in enumerate(table):
            for j, c in enumerate(r):
                c.move_to([xs[j], 1.2 - i * 0.75, 0])
            if i > 0:
                r[0].align_to([-6.2, 0, 0], LEFT)
        self.play(FadeIn(hdr))
        for r in table[1:]:
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.6)
            self.wait(0.4)
        self.wait(0.6)

        why = Text("Both course-blind versions see a 356-yard hole and expect a driver.\nThe layup is scored as a loss even though it was the right play.",
                   font="DejaVu Sans", color=GREY_T, line_spacing=0.9).scale(0.36).shift(DOWN * 2.3)
        self.play(FadeIn(why))
        self.wait(2.0)

        # second example: the drive that works
        sub2 = Text("Hole 1 · driver, fairway, 94 yds left", font="DejaVu Sans", color=GREY_T).scale(0.4).move_to(sub)
        rows2 = [("3.90", "2.78", "+0.12"), ("4.22", "3.00", "+0.22"), ("4.45", "2.96", "+0.49")]
        new_cells = VGroup()
        anims = [Transform(sub, sub2)]
        for r, (a, b_, sg) in zip(table[1:], rows2):
            for cell, txt, col in zip(r[1:], (a, b_, sg), (GOLD_T, GOLD_T, GREEN_T)):
                nc = Text(txt, font="DejaVu Sans", weight=BOLD if cell is r[3] else NORMAL, color=col).scale(0.55 if cell is r[3] else 0.5).move_to(cell)
                anims.append(Transform(cell, nc))
        why2 = Text("When the driver comes off, this model gives it full credit:\nit beat a scratch golfer's best play on this hole by half a stroke, not 0.1.",
                    font="DejaVu Sans", color=GREY_T, line_spacing=0.9).scale(0.36).move_to(why)
        self.play(*anims, Transform(why, why2))
        self.wait(2.6)
        self.play(*[FadeOut(m) for m in [h, sub, table, why]])

    # ---------------------------------------------------------- 5 calibration
    def scene_calibration(self):
        h = Text("Then pin the whole course to its rating", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        self.play(FadeIn(h))

        raw = [4.55, 3.23, 3.89, 3.26, 3.28, 4.37, 3.23, 3.32, 3.95, 3.21, 4.10, 3.00, 3.26, 3.72, 3.14, 4.30, 3.23, 3.11]
        base_y = -2.2
        bars = VGroup()
        for i, v in enumerate(raw):
            b = Rectangle(width=0.5, height=(v - 2.0) * 0.75, color=GOLD_T, fill_opacity=0.7, stroke_width=0)
            b.move_to([-6.1 + i * 0.72, base_y + (v - 2.0) * 0.375, 0])
            bars.add(b)
        axis = Line([-6.5, base_y, 0], [6.5, base_y, 0], color=GREY_T)
        nums = VGroup(*[Text(str(i + 1), font="DejaVu Sans", color=GREY_T).scale(0.28).move_to([-6.1 + i * 0.72, base_y - 0.25, 0]) for i in range(18)])
        ylab = Text("expected strokes, per hole", font="DejaVu Sans", color=GREY_T).scale(0.3).move_to([-5.1, base_y + 2.1, 0])
        self.play(Create(axis), FadeIn(nums), FadeIn(ylab), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.05))
        total = Text("sum of 18 holes = 64.15", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.5).shift(UP * 2.3 + LEFT * 3.4)
        self.play(FadeIn(total))
        self.wait(0.6)

        cr = Text("course rating = 59.9", font="DejaVu Sans", weight=BOLD, color=BLUE_T).scale(0.5).next_to(total, RIGHT, buff=1.2)
        self.play(FadeIn(cr))
        self.wait(0.6)
        gap = Text("gap = 4.25 strokes. But not all of it is the course.", font="DejaVu Sans", color=WHITE_T).scale(0.42).next_to(VGroup(total, cr), DOWN, buff=0.3)
        self.play(FadeIn(gap))
        self.wait(1.2)

        # decomposition
        d1 = Text("A course rating is a scratch golfer's GOOD day: a handicap uses the best 8 of 20 rounds.",
                  font="DejaVu Sans", color=GREY_T).scale(0.36).next_to(gap, DOWN, buff=0.25)
        d2 = MathTex(r"\mathbb{E}[\text{mean of best 8 of 20}] = \mu - 0.93\,\sigma, \quad \sigma \approx 2.6 \;\Rightarrow\; \text{CR} + 2.4 = 62.3 \text{ is an average scratch round}",
                     color=WHITE_T).scale(0.55).next_to(d1, DOWN, buff=0.2)
        self.play(FadeIn(d1))
        self.play(Write(d2))
        self.wait(1.6)

        split = VGroup(Text("2.4  good-day shift (derived)", font="DejaVu Sans", color=BLUE_T).scale(0.4),
                       Text("1.85  the course, spread over 18 holes = −0.10 each", font="DejaVu Sans", color=GREEN_T).scale(0.4)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        self.play(FadeOut(gap), FadeOut(d1), d2.animate.shift(UP * 0.9), ylab.animate.set_opacity(0), run_time=0.6)
        split.next_to(d2, DOWN, buff=0.2)
        self.play(FadeIn(split))
        new_bars = VGroup()
        for i, (b, v) in enumerate(zip(bars, raw)):
            nb = b.copy().set_color(GREEN_T)
            nb.stretch_to_fit_height((v + ADJ - 2.0) * 0.75).move_to([-6.1 + i * 0.72, base_y + (v + ADJ - 2.0) * 0.375, 0])
            new_bars.add(nb)
        self.play(Transform(bars, new_bars), run_time=1.2)
        total2 = Text("sum = 62.3 = CR + 2.4", font="DejaVu Sans", weight=BOLD, color=GREEN_T).scale(0.5).move_to(total)
        self.play(Transform(total, total2))
        self.wait(1.0)
        note = Text("Applied to shots off the green only — putting stays measured straight against the scratch putting data.",
                    font="DejaVu Sans", color=GREY_T).scale(0.34).next_to(axis, DOWN, buff=0.5)
        self.play(FadeIn(note))
        ident = MathTex(r"\sum \text{SG over 18 holes} = (\text{CR} + 2.4) - \text{score}", color=GREEN_T).scale(0.75).next_to(note, DOWN, buff=0.25)
        self.play(Write(ident))
        self.wait(2.2)
        self.play(*[FadeOut(m) for m in [h, bars, axis, nums, ylab, total, cr, d2, split, note, ident]])

    # ---------------------------------------------------------- 6 outro
    def scene_outro(self):
        lines = [("Scratch baseline from published data", GOLD_T),
                 ("Tee shots from a dispersion model that knows where the OB is", BLUE_T),
                 ("Whole course pinned to the USGA rating", GREEN_T)]
        g = VGroup(*[Text(t, font="DejaVu Sans", color=c).scale(0.48) for t, c in lines]).arrange(DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in g], lag_ratio=0.35))
        self.wait(1.2)
        foot = Text("github.com/Eruven/golf-sg-model", font="DejaVu Sans", color=GREY_T).scale(0.4).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(foot))
        self.wait(2.0)
        self.play(FadeOut(g), FadeOut(foot))


# ====================================================================== SHORT CUT
class Short(Scene):
    """~70 s cut for episode 1: expected strokes -> one shot -> the tee model, shown as shots, not tables."""

    def construct(self):
        Explainer.scene_expected_strokes(self)
        self.short_one_shot()
        self.short_tee_shots()

    def short_one_shot(self):
        h = Text("A shot's value is how much it moved that number", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        eq = MathTex(r"\text{SG} = E(\text{start}) - E(\text{end}) - 1", color=WHITE_T).scale(1.05).shift(UP * 1.2)
        self.play(FadeIn(h), Write(eq))
        start = VGroup(Text("102 yds, fairway", font="DejaVu Sans", color=GREY_T).scale(0.4),
                       Text("3.03", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.8)).arrange(DOWN, buff=0.15).shift(LEFT * 3.2 + DOWN * 0.8)
        end = VGroup(Text("22 ft, on the green", font="DejaVu Sans", color=GREY_T).scale(0.4),
                     Text("1.95", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.8)).arrange(DOWN, buff=0.15).shift(RIGHT * 3.2 + DOWN * 0.8)
        arrow = Arrow(start.get_right(), end.get_left(), color=BLUE_T, buff=0.3)
        self.play(FadeIn(start), GrowArrow(arrow), FadeIn(end))
        calc = MathTex(r"3.03 - 1.95 - 1 = ", r"+0.08", color=WHITE_T).scale(0.95).shift(DOWN * 2.3)
        calc[1].set_color(GREEN_T)
        self.play(Write(calc))
        self.wait(1.4)
        self.play(*[FadeOut(m) for m in [h, eq, start, end, arrow, calc]])

    def short_tee_shots(self):
        h = Text("The problem: standard strokes gained doesn't know the course", font="DejaVu Sans", color=WHITE_T).scale(0.5).to_edge(UP)
        self.play(FadeIn(h))

        # top-down hole 1
        YPX, XPX = 0.0146, 0.07
        corridor_w = 45 * XPX
        corr = Rectangle(width=corridor_w, height=5.2, color=GREEN_T, fill_opacity=0.12, stroke_width=1).shift(DOWN * 0.2 + LEFT * 2.6)
        ob_l = Rectangle(width=2.0, height=5.2, color=RED_T, fill_opacity=0.10, stroke_width=0).next_to(corr, LEFT, buff=0)
        ob_r = ob_l.copy().next_to(corr, RIGHT, buff=0)
        obl = Text("OB", font="DejaVu Sans", weight=BOLD, color=RED_T).scale(0.5).move_to(ob_l).shift(DOWN * 1.8)
        obr = obl.copy().move_to(ob_r).shift(DOWN * 1.8)
        tee_pt = corr.get_bottom() + UP * 0.15
        tee = Dot(tee_pt, color=WHITE_T)
        label = Text("Hole 1 · 356 yds · 45 yds wide · OB both sides", font="DejaVu Sans", color=GREY_T).scale(0.38).next_to(corr, DOWN, buff=0.2)
        self.play(FadeIn(corr), FadeIn(ob_l), FadeIn(ob_r), FadeIn(obl), FadeIn(obr), FadeIn(tee), FadeIn(label))

        cx = corr.get_center()[0]; half = corridor_w / 2
        rng = np.random.default_rng(7)

        def shots(dist, sigma, n, col_in):
            pts, dots = [], VGroup()
            xs = rng.normal(0, sigma, n); ys = rng.normal(dist, 9, n)
            for x, y in zip(xs, ys):
                px, py = cx + x * XPX, tee_pt[1] + y * YPX
                inside = abs(x) < 22.5
                dots.add(Dot([px, py, 0], radius=0.055, color=col_in if inside else RED_T))
            return dots

        # driver: 40 shots
        panel = VGroup(Text("Scratch golfer, driver", font="DejaVu Sans", weight=BOLD, color=WHITE_T).scale(0.44),
                       Text("262 yds · lateral σ ≈ 20 yds", font="DejaVu Sans", color=GREY_T).scale(0.36)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(RIGHT * 3.4 + UP * 2.0)
        self.play(FadeIn(panel))
        d_dots = shots(262, 19.6, 40, GOLD_T)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in d_dots], lag_ratio=0.04), run_time=1.6)
        n_ob = sum(1 for d in d_dots if d.get_color().to_hex().lower() == RED_T.lower())
        stat_d = VGroup(Text(f"{n_ob} of 40 out of bounds", font="DejaVu Sans", color=RED_T).scale(0.4),
                        Text("stroke and distance, play 3 from the tee", font="DejaVu Sans", color=GREY_T).scale(0.33),
                        Text("hole averages  4.73", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.5)).arrange(DOWN, aligned_edge=LEFT, buff=0.16).next_to(panel, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(stat_d))
        self.wait(1.4)

        # 5-iron: 40 shots
        self.play(FadeOut(d_dots), run_time=0.4)
        panel2 = VGroup(Text("Scratch golfer, 5-iron", font="DejaVu Sans", weight=BOLD, color=WHITE_T).scale(0.44),
                        Text("185 yds · lateral σ ≈ 13 yds", font="DejaVu Sans", color=GREY_T).scale(0.36)).arrange(DOWN, aligned_edge=LEFT, buff=0.18).move_to(panel, aligned_edge=LEFT)
        self.play(Transform(panel, panel2), FadeOut(stat_d), run_time=0.5)
        i_dots = shots(185, 13.0, 40, BLUE_T)
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in i_dots], lag_ratio=0.04), run_time=1.6)
        n_ob2 = sum(1 for d in i_dots if d.get_color().to_hex().lower() == RED_T.lower())
        stat_i = VGroup(Text(f"{n_ob2} of 40 out of bounds", font="DejaVu Sans", color=BLUE_T).scale(0.4),
                        Text("171 yds left, almost always in play", font="DejaVu Sans", color=GREY_T).scale(0.33),
                        Text("hole averages  4.55", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.5)).arrange(DOWN, aligned_edge=LEFT, buff=0.16).next_to(panel, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(stat_i))
        verdict = Text("Scratch's best play is the 5-iron.\nThis hole is worth 4.55, not 4.0.", font="DejaVu Sans", color=GREEN_T, line_spacing=0.9).scale(0.4).next_to(stat_i, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(FadeIn(verdict))
        self.wait(1.8)

        # one driver comes in, in play, 94 yds left
        self.play(FadeOut(i_dots), FadeOut(panel), FadeOut(stat_i), FadeOut(verdict), run_time=0.5)
        h2 = Text("Now I hit driver here, and it comes off", font="DejaVu Sans", color=WHITE_T).scale(0.5).to_edge(UP)
        self.play(Transform(h, h2))
        land = [cx + 6 * XPX, tee_pt[1] + 262 * YPX, 0]
        path = ArcBetweenPoints(tee_pt, land, angle=-0.35, color=WHITE_T, stroke_width=2)
        ball = Dot(land, radius=0.09, color=WHITE_T)
        self.play(Create(path), run_time=0.9)
        self.play(FadeIn(ball, scale=0.3))
        left = Text("94 yds left", font="DejaVu Sans", color=GREY_T).scale(0.36).next_to(ball, RIGHT, buff=0.15)
        self.play(FadeIn(left))
        self.wait(0.4)

        q = Text("What was that shot worth?", font="DejaVu Sans", weight=BOLD, color=WHITE_T).scale(0.46).move_to(RIGHT * 3.4 + UP * 2.0)
        self.play(FadeIn(q))
        rows = [("Standard SG, tour baseline", "+0.12", GREY_T, 0.5),
                ("Scratch baseline, any course", "+0.22", GREY_T, 0.5),
                ("This model, this hole", "+0.49", GREEN_T, 0.7)]
        tags = VGroup()
        for name, v, col, sc in rows:
            tags.add(VGroup(Text(name, font="DejaVu Sans", color=GREY_T if col == GREY_T else WHITE_T).scale(0.38),
                            Text(v, font="DejaVu Sans", weight=BOLD, color=col).scale(sc)).arrange(RIGHT, buff=0.35))
        tags.arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(q, DOWN, buff=0.45, aligned_edge=LEFT)
        for t in tags:
            t[1].align_to([6.6, 0, 0], RIGHT)
        for t in tags:
            self.play(FadeIn(t, shift=RIGHT * 0.2), run_time=0.5)
            self.wait(0.5)
        why = Text("The other two see a 356-yard hole and expect a driver.\nThis one knows how often a driver here ends up OB,\nso a drive that stays in play gets the credit it earned.",
                   font="DejaVu Sans", color=GREY_T, line_spacing=0.9).scale(0.34).next_to(tags, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(FadeIn(why))
        self.wait(2.6)
        foot = Text("github.com/Eruven/golf-sg-model", font="DejaVu Sans", color=GREY_T).scale(0.34).to_edge(DOWN, buff=0.25).to_edge(RIGHT, buff=0.4)
        self.play(FadeIn(foot))
        self.wait(1.2)
        self.play(*[FadeOut(m) for m in self.mobjects])
