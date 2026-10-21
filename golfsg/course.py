"""Course definition and calibration of hole expectations to the course rating."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .baseline import Baseline
from .params import SCRATCH_CLUBS, Club, Params
from .tee import tee_model


@dataclass
class Hole:
    number: int
    par: int
    yards: float
    stroke_index: int
    width: float | None = None      # corridor width, yards (par 4/5 only)
    trouble: str = "X"              # X, OB, OBR, OBL


@dataclass
class Course:
    name: str
    tees: str
    course_rating: float
    slope: float
    holes: list[Hole]
    default_width: float = 45.0

    @classmethod
    def from_json(cls, path: str | Path) -> "Course":
        d = json.loads(Path(path).read_text())
        holes = [Hole(**h) for h in d["holes"]]
        return cls(d["name"], d["tees"], d["course_rating"], d["slope"], holes, d.get("default_width", 45.0))

    @property
    def par(self) -> int:
        return sum(h.par for h in self.holes)


@dataclass
class HoleValue:
    hole: Hole
    raw: float                     # scratch expected strokes before calibration
    best_club: str | None
    club_table: dict[str, float]
    weight: float
    adjustment: float
    adjusted: float


@dataclass
class CalibratedCourse:
    course: Course
    values: list[HoleValue]
    target: float
    total_adjustment: float

    def by_number(self, n: int) -> HoleValue:
        return self.values[n - 1]


def calibrate(course: Course, base: Baseline, clubs: list[Club] | None = None,
              params: Params | None = None) -> CalibratedCourse:
    """Hole-level scratch expectations, then spread (target - raw total) across holes.

    weight_h = (1 - lambda)/18 + lambda * (19 - SI_h)/171, which sums to 1 for any lambda.
    """
    p = params or base.p
    clubs = clubs or SCRATCH_CLUBS
    raws, bests, tables = [], [], []
    for h in course.holes:
        if h.par == 3:
            raws.append(base.F(h.yards) - p.teed_ball_bonus); bests.append(None); tables.append({})
        else:
            w = h.width if h.width is not None else course.default_width
            e, best, table = tee_model(h.yards, w, h.trouble, clubs, base, p)
            raws.append(e); bests.append(best.name); tables.append(table)
    target = course.course_rating + p.good_day_gap
    n = len(course.holes)
    si_sum = sum(range(1, n + 1))
    weights = [(1 - p.si_weight) / n + p.si_weight * (n + 1 - h.stroke_index) / si_sum for h in course.holes]
    gap = target - sum(raws)
    values = [HoleValue(h, r, b, t, w, gap * w, r + gap * w)
              for h, r, b, t, w in zip(course.holes, raws, bests, tables, weights)]
    return CalibratedCourse(course, values, target, gap)
