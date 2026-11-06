from manim import *
import numpy as np

BG = "#0f1115"; WHITE_T = "#ECECEC"; GREY_T = "#8A8F98"; GOLD_T = "#F2C14E"; BLUE_T = "#5DA9E9"
RED_T = "#E86A5A"; GREEN_T = "#6CCB8B"
config.background_color = BG

# ---------------- physics: two sticks and a free hinge ----------------
L1, L2 = 0.62, 1.05
TH0, THI = np.radians(150), np.radians(270)
HINGE0 = np.radians(95)

def make_profile(brake, tb=0.17, T=0.26):
    ts = np.linspace(0, T, 4001)
    sm = lambda x: np.clip(x, 0, 1)**2 * (3 - 2 * np.clip(x, 0, 1))
    w = np.where(ts < tb, 0.15 + 0.85 * sm(ts / tb), 1.0 + (-0.7 if brake else 0.35) * sm((ts - tb) / (T - tb)))
    ang = np.concatenate([[0], np.cumsum((w[1:] + w[:-1]) / 2 * np.diff(ts))])
    ang = ang / ang[-1] * (THI - TH0) + TH0
    slope = (ang[-1] - ang[-2]) / (ts[1] - ts[0])
    return lambda t: np.interp(t, ts, ang) if t <= T else ang[-1] + (t - T) * slope

def simulate(profile, T, dt=1e-4):
    phi = profile(0) - HINGE0; om = (profile(dt) - profile(0)) / dt
    hand = lambda t: L1 * np.array([np.cos(profile(t)), np.sin(profile(t))])
    rows = []; t = 0.0
    while t <= T:
        acc = (hand(t + dt) - 2 * hand(t) + hand(t - dt)) / dt**2
        u = np.array([np.cos(phi), np.sin(phi)])
        om += -(u[0] * acc[1] - u[1] * acc[0]) / L2 * dt; phi += om * dt
        if profile(t) - phi > HINGE0 and om < (profile(t + dt) - profile(t)) / dt:
            phi = profile(t) - HINGE0; om = (profile(t + dt) - profile(t)) / dt
        rows.append((t, profile(t), phi)); t += dt
    a = np.array(rows)
    hx, hy = L1 * np.cos(a[:, 1]), L1 * np.sin(a[:, 1])
    cx, cy = hx + L2 * np.cos(a[:, 2]), hy + L2 * np.sin(a[:, 2])
    vh = np.hypot(np.gradient(hx, dt), np.gradient(hy, dt)) * 2.237
    vc = np.hypot(np.gradient(cx, dt), np.gradient(cy, dt)) * 2.237
    return dict(t=a[:, 0], th=a[:, 1], phi=a[:, 2], vh=vh, vc=vc)

PA = make_profile(False); PB = make_profile(True)
SA = simulate(PA, 0.262); SB = simulate(PB, 0.30)
iA = len(SA["t"]) - 1                       # hands at the ball
iBh = np.argmax(SB["th"] >= THI)            # brake case: hands at the ball
iBc = np.argmax(SB["phi"] >= THI)           # brake case: club square at the ball
TB_END = SB["t"][iBc]

def at(S, t):
    i = min(int(round(t / 1e-4)), len(S["t"]) - 1)
    return S["th"][i], S["phi"][i], S["vh"][i], S["vc"][i]

SC = 1.55  # manim units per metre

def golfer(hub, th, phi, faint=False):
    hub = np.array(hub)
    hand = hub + SC * L1 * np.array([np.cos(th), np.sin(th), 0])
    head = hand + SC * L2 * np.array([np.cos(phi), np.sin(phi), 0])
    sh = 0.28
    body_col = GREY_T
    head_c = Circle(radius=0.18, color=body_col, stroke_width=2).move_to(hub + UP * 0.42)
    gy = SC * (L1 + L2) + 0.1
    torso = Line(hub, hub + DOWN * 1.15, color=body_col, stroke_width=2)
    legs = VGroup(Line(hub + DOWN * 1.15, hub + DOWN * gy + LEFT * 0.35, color=body_col, stroke_width=2),
                  Line(hub + DOWN * 1.15, hub + DOWN * gy + RIGHT * 0.35, color=body_col, stroke_width=2))
    tri = Polygon(hub + LEFT * sh, hub + RIGHT * sh, hand, color=BLUE_T, fill_opacity=0.25, stroke_width=3)
    club = Line(hand, head, color=GOLD_T, stroke_width=5)
    hinge = Dot(hand, radius=0.07, color=WHITE_T)
    clubhead = Dot(head, radius=0.08, color=GOLD_T)
    g = VGroup(head_c, torso, legs, tri, club, hinge, clubhead)
    if faint: g.set_opacity(0.35)
    return g


class SwingModel(Scene):
    def construct(self):
        self.title()
        self.rope_vs_stick()
        self.the_model()
        self.compare()
        self.speed_graph()
        self.outro()

    def title(self):
        t = Text("Sticks, not ropes", font="DejaVu Sans", weight=BOLD, color=WHITE_T).scale(0.95)
        s = Text("the golf swing as two sticks and a hinge", font="DejaVu Sans", color=GREY_T).scale(0.45).next_to(t, DOWN, buff=0.3)
        self.play(FadeIn(t, shift=UP * 0.2), FadeIn(s))
        self.wait(1.4)
        self.play(FadeOut(t), FadeOut(s))

    def rope_vs_stick(self):
        h = Text("Most lessons picture the swing as a whip", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        self.play(FadeIn(h))
        rope = FunctionGraph(lambda x: 0.25 * np.sin(3 * x) * np.exp(0.15 * x), x_range=[-2, 2], color=RED_T, stroke_width=4).shift(LEFT * 3.3 + UP * 0.2)
        rl = VGroup(Text("Rope", font="DejaVu Sans", weight=BOLD, color=RED_T).scale(0.5),
                    Text("can only pull.\nNothing to brace against,\nso the only speed is a flick\nof the hands.", font="DejaVu Sans", color=GREY_T, line_spacing=0.9).scale(0.36)
                    ).arrange(DOWN, buff=0.25).next_to(rope, DOWN, buff=0.5)
        stick1 = Line(ORIGIN, RIGHT * 2.0, color=BLUE_T, stroke_width=8)
        stick2 = Line(RIGHT * 2.0, RIGHT * 2.0 + rotate_vector(RIGHT * 1.6, -PI / 2), color=GOLD_T, stroke_width=6)
        joint = Dot(RIGHT * 2.0, color=WHITE_T)
        stick = VGroup(stick1, stick2, joint).move_to(RIGHT * 3.3 + UP * 0.2)
        sl = VGroup(Text("Sticks + hinge", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.5),
                    Text("can push, brace and hold an angle.\nWhen one stick slows,\nthe next one speeds up.", font="DejaVu Sans", color=GREY_T, line_spacing=0.9).scale(0.36)
                    ).arrange(DOWN, buff=0.25).next_to(stick, DOWN, buff=0.5)
        self.play(Create(rope), FadeIn(rl))
        self.wait(1.2)
        self.play(Create(stick), FadeIn(sl))
        self.wait(2.2)
        self.play(*[FadeOut(m) for m in [h, rope, rl, stick, sl]])

    def the_model(self):
        h = Text("Body, arm triangle, club, wrist hinge", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        self.play(FadeIn(h))
        hub = np.array([0, 0.7, 0])
        th = ValueTracker(np.radians(-90)); hg = ValueTracker(0.0)
        g = always_redraw(lambda: golfer(hub, th.get_value(), th.get_value() - hg.get_value()))
        ground = Line(LEFT * 3, RIGHT * 3, color=GREY_T, stroke_width=1).move_to(hub + DOWN * (SC * (L1 + L2) + 0.1))
        self.play(FadeIn(g), Create(ground))
        lbl = VGroup(
            Text("arm triangle (one rigid piece)", font="DejaVu Sans", color=BLUE_T).scale(0.34).move_to(LEFT * 2.9 + UP * 0.3),
            Text("wrist hinge", font="DejaVu Sans", color=WHITE_T).scale(0.34).move_to(RIGHT * 1.3 + DOWN * 0.26),
            Text("club (a stick)", font="DejaVu Sans", color=GOLD_T).scale(0.34).move_to(RIGHT * 1.3 + DOWN * 1.2))
        self.play(FadeIn(lbl))
        self.wait(1.0)
        self.play(FadeOut(lbl))
        cap = Text("Backswing: the triangle turns, the wrists set to about 90°", font="DejaVu Sans", color=GREY_T).scale(0.38).to_edge(DOWN)
        self.play(FadeIn(cap))
        self.play(th.animate.set_value(TH0), hg.animate.set_value(HINGE0), run_time=2.2, rate_func=smooth)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in [h, g, ground, cap]])

    def compare(self):
        h = Text("Same downswing start. Two endings.", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        self.play(FadeIn(h))
        hubA, hubB = np.array([-3.4, 0.55, 0]), np.array([3.4, 0.55, 0])
        tA = Text("Hands keep speeding up", font="DejaVu Sans", color=RED_T).scale(0.4).move_to([-3.4, 3.0, 0])
        tB = Text("Push up, triangle slows down", font="DejaVu Sans", color=GREEN_T).scale(0.4).move_to([3.4, 3.0, 0])
        balls = VGroup(*[Dot(hb + DOWN * SC * (L1 + L2) + DOWN * 0.03, radius=0.07, color=WHITE_T) for hb in (hubA, hubB)])
        gl = VGroup(*[Line(hb + DOWN * (SC * (L1 + L2) + 0.1) + LEFT * 2.6, hb + DOWN * (SC * (L1 + L2) + 0.1) + RIGHT * 2.6, color=GREY_T, stroke_width=1) for hb in (hubA, hubB)])
        T = ValueTracker(0.0)
        gA = always_redraw(lambda: golfer(hubA, *at(SA, min(T.get_value(), SA["t"][-1]))[:2]))
        gB = always_redraw(lambda: golfer(hubB, *at(SB, min(T.get_value(), TB_END))[:2]))
        self.play(FadeIn(tA), FadeIn(tB), FadeIn(gA), FadeIn(gB), FadeIn(balls), FadeIn(gl))
        tagA = Text("", font="DejaVu Sans").scale(0.3)
        # run to the moment the hands reach the ball (left case)
        self.play(T.animate.set_value(SA["t"][-1]), run_time=4.5, rate_func=linear)
        relA = np.degrees(SA["th"][-1] - SA["phi"][-1]); relB = np.degrees(SB["th"][iBh] - SB["phi"][iBh])
        nA = VGroup(Text("Hands at the ball,", font="DejaVu Sans", color=WHITE_T).scale(0.34),
                    Text(f"club still {relA:.0f}° behind", font="DejaVu Sans", weight=BOLD, color=RED_T).scale(0.4),
                    Text("arrives late and open", font="DejaVu Sans", color=GREY_T).scale(0.34)).arrange(DOWN, buff=0.12).move_to(hubA + DOWN * 3.35)
        self.play(FadeIn(nA))
        self.play(T.animate.set_value(TB_END), run_time=1.2, rate_func=linear)
        vB = SB["vc"][iBc]
        nB = VGroup(Text("The club catches up and squares", font="DejaVu Sans", color=WHITE_T).scale(0.34),
                    Text("at full speed", font="DejaVu Sans", weight=BOLD, color=GREEN_T).scale(0.4),
                    Text("hands just ahead of the ball", font="DejaVu Sans", color=GREY_T).scale(0.34)).arrange(DOWN, buff=0.12).move_to(hubB + DOWN * 3.35)
        self.play(FadeIn(nB))
        self.wait(3.0)
        self.play(*[FadeOut(m) for m in [h, tA, tB, gA, gB, balls, gl, nA, nB]])

    def speed_graph(self):
        h = Text("Where the speed comes from", font="DejaVu Sans", color=WHITE_T).scale(0.55).to_edge(UP)
        self.play(FadeIn(h))
        t = SB["t"][:iBc + 1]; vh = SB["vh"][:iBc + 1]; vc = SB["vc"][:iBc + 1]
        top = vc.max() * 1.12
        ax = Axes(x_range=[0, round(t[-1] + 0.02, 2), 0.1], y_range=[0, top, top / 4], x_length=8.5, y_length=4.2,
                  x_axis_config={"color": GREY_T, "include_numbers": True, "font_size": 20},
                  y_axis_config={"color": GREY_T, "include_numbers": False},
                  tips=False).shift(DOWN * 0.4 + LEFT * 0.6)
        xl = Text("seconds into the downswing", font="DejaVu Sans", color=GREY_T).scale(0.3).next_to(ax, DOWN, buff=0.15)
        yl = Text("speed", font="DejaVu Sans", color=GREY_T).scale(0.3).next_to(ax.y_axis, UP, buff=0.1)
        cH = ax.plot_line_graph(t[::40], vh[::40], add_vertex_dots=False, line_color=BLUE_T, stroke_width=4)
        cC = ax.plot_line_graph(t[::40], vc[::40], add_vertex_dots=False, line_color=GOLD_T, stroke_width=4)
        lH = Text("hands", font="DejaVu Sans", color=BLUE_T).scale(0.36).next_to(ax.c2p(t[int(len(t) * 0.35)], vh[int(len(t) * 0.35)]), UP, buff=0.15)
        lC = Text("clubhead", font="DejaVu Sans", color=GOLD_T).scale(0.36).next_to(ax.c2p(t[-1], vc[-1]), LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl))
        self.play(Create(cH), FadeIn(lH), run_time=1.5)
        self.play(Create(cC), FadeIn(lC), run_time=1.8)
        k = np.argmax(vh)
        brace = DashedLine(ax.c2p(t[k], 0), ax.c2p(t[k], top), color=GREY_T)
        note = Text("hands start slowing here,\nclubhead keeps accelerating", font="DejaVu Sans", color=WHITE_T, line_spacing=0.9).scale(0.34).next_to(ax.c2p(t[k], top * 0.88), LEFT, buff=0.2)
        self.play(Create(brace), FadeIn(note))
        self.wait(3.0)
        cap = Text("Two sticks and a free hinge: when the first slows, the second speeds up.", font="DejaVu Sans", color=GREY_T).scale(0.34).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(cap))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in [h, ax, xl, yl, cH, cC, lH, lC, brace, note, cap]])

    def outro(self):
        lines = VGroup(
            Text("Push up to brace the triangle.", font="DejaVu Sans", color=WHITE_T).scale(0.55),
            Text("Let it slow down.", font="DejaVu Sans", color=WHITE_T).scale(0.55),
            Text("The club releases itself.", font="DejaVu Sans", weight=BOLD, color=GOLD_T).scale(0.6)).arrange(DOWN, buff=0.35)
        foot = Text("simple two-link model: rigid arm, free wrist hinge, swing plane only", font="DejaVu Sans", color=GREY_T).scale(0.28).to_edge(DOWN, buff=0.3)
        for l in lines:
            self.play(FadeIn(l, shift=UP * 0.15), run_time=0.7)
            self.wait(0.4)
        self.play(FadeIn(foot))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in [lines, foot]])
