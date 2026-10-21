"""Score a shot log against the calibrated scratch baseline.

A shot: (hole, start_lie, start_dist, end_lie, end_dist, penalty). G distances in feet, others in yards.
SG = E'(start) - E'(end) - 1 - penalty, where E' = E + a_h * w(pos) and
w = 1 on the tee, 0 on the green, clip[(E - g0)/(E_tee - g0), 0, 1] elsewhere,
so a hole's SG telescopes to E_raw + a_h - strokes and putting carries no course adjustment.
"""
from __future__ import annotations

from dataclasses import dataclass

from .baseline import Baseline
from .course import CalibratedCourse


@dataclass
class Shot:
    hole: int
    start_lie: str
    start_dist: float
    end_lie: str
    end_dist: float | None = None
    penalty: int = 0
    note: str = ""


@dataclass
class ScoredShot:
    shot: Shot
    category: str
    e_start: float
    e_end: float
    sg: float


CATS = ("OTT", "APP", "ARG", "PUTT")


def _category(shot: Shot, par: int) -> str:
    lie = shot.start_lie.upper()
    if lie == "G":
        return "PUTT"
    if lie == "T" and par > 3:
        return "OTT"
    return "ARG" if shot.start_dist <= 30 else "APP"


def _raw(base: Baseline, cal: CalibratedCourse, hole: int, lie: str, dist: float | None) -> float:
    lie = lie.upper()
    hv = cal.by_number(hole)
    if lie == "H":
        return 0.0
    if lie == "T":
        if hv.hole.par == 3:
            return base.F(dist) - base.p.teed_ball_bonus
        return hv.raw
    return base.E(lie, dist)


def _weight(base: Baseline, cal: CalibratedCourse, hole: int, lie: str, e: float) -> float:
    lie = lie.upper()
    if lie in ("G", "H"):
        return 0.0
    if lie == "T":
        return 1.0
    tee = cal.by_number(hole).raw
    g0 = base.p.g0
    return min(1.0, max(0.0, (e - g0) / max(tee - g0, 0.01)))


def score_shot(shot: Shot, base: Baseline, cal: CalibratedCourse) -> ScoredShot:
    hv = cal.by_number(shot.hole)
    rs = _raw(base, cal, shot.hole, shot.start_lie, shot.start_dist)
    re = _raw(base, cal, shot.hole, shot.end_lie, shot.end_dist)
    es = rs + hv.adjustment * _weight(base, cal, shot.hole, shot.start_lie, rs)
    ee = re + hv.adjustment * _weight(base, cal, shot.hole, shot.end_lie, re)
    return ScoredShot(shot, _category(shot, hv.hole.par), es, ee, es - ee - 1 - shot.penalty)


def score_round(shots: list[Shot], base: Baseline, cal: CalibratedCourse) -> dict:
    scored = [score_shot(s, base, cal) for s in shots]
    totals = {c: 0.0 for c in CATS}
    for s in scored:
        totals[s.category] += s.sg
    strokes = len(shots) + sum(s.penalty for s in shots)
    holes = len({s.hole for s in shots if s.end_lie.upper() == "H"})
    return {"shots": scored, "by_category": totals, "total": sum(totals.values()),
            "strokes": strokes, "holes": holes}
