"""Model parameters and the published scratch-golfer anchor data.

Every number here is either PUBLISHED (with its source in the docstring/comments),
DERIVED from a published figure (the derivation is stated), or an ASSUMPTION.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Params:
    """Tunable assumptions. Defaults reproduce the Fox Creek workbook."""

    # --- approach model ---
    jensen: float = 0.70        # effective putt distance = jensen * mean on-green proximity (ASSUMPTION)
    rough_gir_factor: float = 0.80   # Shot Scope: fairway-vs-rough GIR advantage "up to 25%"
    rough_prox_factor: float = 1.25  # golfity estimate: rough adds 30-40% to proximity (ASSUMPTION)
    rough_miss_add: float = 0.10     # ASSUMPTION
    sand_gir_factor: float = 0.65    # fairway bunker, >50 yds (ASSUMPTION)
    sand_prox_factor: float = 1.30   # ASSUMPTION
    sand_miss_add: float = 0.20      # ASSUMPTION
    rough_arg_add: float = 0.20      # chip from rough vs fairway/fringe (ASSUMPTION)
    layup_fairway_share: float = 0.70  # where a layup/advance finishes (ASSUMPTION)
    layup_from_fairway: float = 220.0  # scratch 3-wood/hybrid advance (ASSUMPTION)
    layup_from_rough: float = 190.0
    layup_from_sand: float = 170.0
    layup_min_leave: float = 30.0    # a deliberate layup never leaves less than this
    recovery_advance: float = 100.0  # yards gained by a punch-out (ASSUMPTION)
    recovery_penalty: float = 0.10   # ASSUMPTION
    teed_ball_bonus: float = 0.0     # par-3 tee shot vs same-length fairway shot
    # --- calibration ---
    good_day_gap: float = 0.0        # 0 = calibrate to the course rating (good-day scratch); ~2.5 = average scratch
    si_weight: float = 0.0           # 0 = spread the course adjustment evenly, 1 = fully by stroke index
    g0: float = 1.85                 # off-green anchor for spreading a hole's adjustment across shots
    # --- tee model ---
    tee_fairway_share: float = 0.70  # in-play tee shots: fairway/rough blend (ASSUMPTION)


@dataclass
class Club:
    name: str
    distance: float      # typical in-play total distance, yards
    sigma_pct: float     # lateral std dev as a fraction of distance


# Scratch tee clubs. Distances: Shot Scope P-avg (solid strikes) x 0.92 to approximate a plain average
# (Shot Scope hybrid data: 3H P-avg 219 vs average 197; Arccos 0-4.9 band averages 244 all ages).
# Dispersion: DERIVED. Arccos (Stagner): 7% of 0-5 index drives finish >40 yds from fairway centre
# -> sigma ~22 yds; tour "65-70 yd cone" -> ~16-18 yds; scratch set ~20 yds. 3-wood: Shot Scope shows
# scratch 3-wood hits only ~1% more fairways than driver despite ~18 yds less -> similar absolute spread.
SCRATCH_CLUBS = [
    Club("driver", 262, 0.075),
    Club("3-wood", 245, 0.080),
    Club("3-hybrid", 203, 0.075),   # sigma ASSUMPTION
    Club("5-iron", 185, 0.070),     # sigma ASSUMPTION
]


@dataclass
class ScratchData:
    """Anchor tables for a scratch (0 handicap) golfer.

    putting: (feet, P(1-putt), P(3-putt), P(4-putt))
      Shot Scope 0-hcp make %: 0-3 ft 98%, 3-6 76%, 6-9 49%, 9-12 34%, 12-18 19-25%, 18-24 12-15%,
      24-30 7-8%, 30+ 4%. Three-putts: Arccos 1-5 index 9.4% from 20-25 ft, 19.6% from 25+ ft;
      Arccos/Stagner scratch ~25% from 36-40 ft; Shot Scope scratch 3% of holes, 4.6 ft left from 30 ft.
    approach: (yards, GIR, on-green proximity ft, E after a miss) for a fairway lie
      Chosen so GIR*on_green + (1-GIR)*miss reproduces Shot Scope scratch proximity incl. misses:
      50-100 yds 26 ft, 100-150 38 ft, 150-200 54 ft, 200+ 92 ft; overall GIR 52-59%.
    arg: (yards, E) fairway/fringe lie inside 50 yds
      Shot Scope scratch up-and-down <25 yds 63%, 25-50 yds 32%; E ~ 3 - U&D + 0.03.
    sand: (yards, E) greenside bunker; Shot Scope scratch sand save 37%.
    """

    putting: list[tuple[float, float, float, float]] = field(default_factory=lambda: [
        (1, 1.00, 0, 0), (2, 0.99, 0, 0), (3, 0.94, 0, 0), (4, 0.84, 0.001, 0), (5, 0.73, 0.002, 0),
        (6, 0.62, 0.003, 0), (8, 0.47, 0.006, 0), (10, 0.36, 0.012, 0), (12, 0.29, 0.02, 0),
        (15, 0.22, 0.03, 0), (20, 0.14, 0.055, 0.001), (25, 0.095, 0.09, 0.002), (30, 0.065, 0.13, 0.003),
        (40, 0.035, 0.20, 0.005), (50, 0.025, 0.27, 0.01), (60, 0.018, 0.34, 0.015),
        (80, 0.010, 0.45, 0.025), (100, 0.005, 0.53, 0.035)])
    approach: list[tuple[float, float, float, float]] = field(default_factory=lambda: [
        (50, 0.80, 14, 2.45), (75, 0.75, 17, 2.48), (100, 0.68, 21, 2.50), (125, 0.62, 25, 2.55),
        (150, 0.55, 30, 2.60), (175, 0.47, 36, 2.65), (200, 0.38, 42, 2.72), (225, 0.30, 48, 2.80),
        (250, 0.22, 55, 2.90)])
    arg: list[tuple[float, float]] = field(default_factory=lambda: [
        (5, 2.18), (10, 2.30), (15, 2.38), (20, 2.44), (25, 2.50), (30, 2.58), (40, 2.68), (50, 2.80)])
    sand: list[tuple[float, float]] = field(default_factory=lambda: [
        (5, 2.55), (10, 2.62), (15, 2.68), (20, 2.75), (30, 2.86), (40, 3.00), (50, 3.08)])


# Approximate PGA Tour values (Broadie, Every Shot Counts). Reference only; not used in calculations.
TOUR_REFERENCE = {
    ("G", 3): 1.04, ("G", 6): 1.34, ("G", 10): 1.61, ("G", 15): 1.78, ("G", 20): 1.87, ("G", 30): 1.98,
    ("G", 40): 2.06, ("G", 60): 2.21,
    ("F", 10): 2.18, ("F", 20): 2.40, ("F", 30): 2.52, ("F", 50): 2.66, ("F", 100): 2.80, ("F", 150): 2.95,
    ("F", 200): 3.19, ("F", 250): 3.52, ("F", 300): 3.78,
    ("R", 20): 2.59, ("R", 100): 3.02, ("R", 150): 3.19, ("R", 200): 3.42,
    ("S", 20): 2.53, ("X", 150): 3.80,
}
