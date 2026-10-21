"""Tee-shot decision model for par 4s and 5s.

E(club) = 1 + P_in * E_in + P_tree * E_recovery + P_OB * (1 + E)   (OB = stroke and distance)
      => E = (1 + P_in*E_in + P_tree*E_X + P_OB) / (1 - P_OB)
P_in = 2*Phi(width/2 / sigma) - 1 with sigma = sigma_pct * club distance; misses split evenly left/right.
Trouble codes: "X" trees both sides, "OB" OB both sides, "OBR"/"OBL" OB one side, trees the other.
"""
from __future__ import annotations

from math import erf, sqrt

from .baseline import Baseline
from .params import Club, Params


def phi(z: float) -> float:
    return 0.5 * (1 + erf(z / sqrt(2)))


def p_in_play(width: float, sigma: float) -> float:
    return 2 * phi((width / 2) / sigma) - 1


def club_expectation(hole_yards: float, width: float, trouble: str, club: Club,
                     base: Baseline, params: Params | None = None) -> float:
    p = params or base.p
    sigma = club.sigma_pct * club.distance
    pin = p_in_play(width, sigma)
    leave = max(hole_yards - club.distance, 15)
    e_in = p.tee_fairway_share * base.F(leave) + (1 - p.tee_fairway_share) * base.R(leave)
    e_x = base.X(leave)
    trouble = trouble.upper()
    if trouble == "OB":
        pob = 1 - pin
    elif trouble in ("OBR", "OBL"):
        pob = (1 - pin) / 2
    else:
        pob = 0.0
    ptree = 1 - pin - pob
    return (1 + pin * e_in + ptree * e_x + pob) / (1 - pob)


def tee_model(hole_yards: float, width: float, trouble: str, clubs: list[Club],
              base: Baseline, params: Params | None = None) -> tuple[float, Club, dict[str, float]]:
    """Return (best E, best club, {club name: E}) for a par 4/5 tee shot."""
    table = {c.name: club_expectation(hole_yards, width, trouble, c, base, params) for c in clubs}
    best = min(clubs, key=lambda c: table[c.name])
    return table[best.name], best, table
