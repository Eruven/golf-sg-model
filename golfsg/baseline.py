"""Scratch expected-strokes-to-hole-out tables, built from ScratchData and Params.

Mirrors the 'Baseline' tab of the workbook: yards are rounded to the nearest 5 (5..600),
feet to the nearest 1 (1..100); anchors are linearly interpolated with constant extrapolation.
"""
from __future__ import annotations

from functools import lru_cache

from .params import Params, ScratchData

LIES = ("F", "R", "S", "X")


def _interp(xs: list[float], ys: list[float], x: float) -> float:
    """Linear interpolation with constant extrapolation (same as the sheet's INDEX/MATCH formula)."""
    if x <= xs[0]:
        return ys[0]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


def round5(yards: float) -> int:
    return int(min(max(round(yards / 5) * 5, 5), 600))


class Baseline:
    def __init__(self, data: ScratchData | None = None, params: Params | None = None):
        self.data = data or ScratchData()
        self.p = params or Params()
        d = self.data
        self._pf = [r[0] for r in d.putting]
        self._pe = [2 - p1 + p3 + p4 for _, p1, p3, p4 in d.putting]
        self._ax = [r[0] for r in d.approach]
        self._ag = [r[1] for r in d.approach]
        self._ap = [r[2] for r in d.approach]
        self._am = [r[3] for r in d.approach]
        self._cx = [r[0] for r in d.arg]
        self._ce = [r[1] for r in d.arg]
        self._sx = [r[0] for r in d.sand]
        self._se = [r[1] for r in d.sand]

    # ---- putting ----
    def putt(self, feet: float) -> float:
        """E(putts) from `feet`, rounded to the nearest foot, clipped to 1..100."""
        f = min(max(round(feet), 1), 100)
        return _interp(self._pf, self._pe, f)

    # ---- helpers ----
    def _gir(self, d): return _interp(self._ax, self._ag, d)
    def _prox(self, d): return _interp(self._ax, self._ap, d)
    def _miss(self, d): return _interp(self._ax, self._am, d)

    def _approach(self, d, gir_f=1.0, prox_f=1.0, miss_add=0.0) -> float:
        g = self._gir(d) * gir_f
        return 1 + g * self.putt(self.p.jensen * self._prox(d) * prox_f) + (1 - g) * (self._miss(d) + miss_add)

    def _layup(self, d, adv, add=0.0) -> float:
        L = max(d - adv, self.p.layup_min_leave)
        s = self.p.layup_fairway_share
        return 1 + s * self.F(L) + (1 - s) * self.R(L) + add

    # ---- tables (yards rounded to 5) ----
    @lru_cache(maxsize=None)
    def F(self, yards: float) -> float:
        d = round5(yards)
        if d <= 50:
            return _interp(self._cx, self._ce, d)
        lay = self._layup(d, self.p.layup_from_fairway)
        if d <= 250:
            return min(self._approach(d), lay)
        return lay

    @lru_cache(maxsize=None)
    def R(self, yards: float) -> float:
        d = round5(yards)
        p = self.p
        if d <= 50:
            return self.F(d) + p.rough_arg_add
        lay = self._layup(d, p.layup_from_rough, p.rough_miss_add)
        if d <= 250:
            return min(self._approach(d, p.rough_gir_factor, p.rough_prox_factor, p.rough_miss_add), lay)
        return lay

    @lru_cache(maxsize=None)
    def S(self, yards: float) -> float:
        d = round5(yards)
        p = self.p
        if d <= 50:
            return _interp(self._sx, self._se, d)
        lay = self._layup(d, p.layup_from_sand, p.sand_miss_add)
        if d <= 250:
            return min(self._approach(d, p.sand_gir_factor, p.sand_prox_factor, p.sand_miss_add), lay)
        return lay

    @lru_cache(maxsize=None)
    def X(self, yards: float) -> float:
        d = round5(yards)
        L = max(d - self.p.recovery_advance, 15)
        return 1 + self.p.recovery_penalty + 0.6 * self.F(L) + 0.4 * self.R(L)

    def E(self, lie: str, dist: float) -> float:
        """Expected strokes from (lie, distance). G in feet, everything else in yards. H = holed."""
        lie = lie.upper()
        if lie == "H":
            return 0.0
        if lie == "G":
            return self.putt(dist)
        if lie == "T":  # par-3 style tee shot at this yardage
            return self.F(dist) - self.p.teed_ball_bonus
        return {"F": self.F, "R": self.R, "S": self.S, "X": self.X}[lie](dist)
