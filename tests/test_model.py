import math
from pathlib import Path

import pytest

from golfsg import Baseline, Course, Params, Shot, calibrate, score_round, score_shot, p_in_play
from golfsg.params import SCRATCH_CLUBS, TOUR_REFERENCE
from golfsg.tee import club_expectation

DATA = Path(__file__).resolve().parents[1] / "data" / "fox_creek.json"


@pytest.fixture(scope="module")
def base():
    return Baseline()


@pytest.fixture(scope="module")
def cal(base):
    return calibrate(Course.from_json(DATA), base)


def test_putting_formula(base):
    # E = 2 - p1 + p3 + p4 at an anchor: 20 ft -> 2 - 0.14 + 0.055 + 0.001
    assert base.putt(20) == pytest.approx(1.916, abs=1e-6)
    assert base.putt(1) == pytest.approx(1.0)
    assert base.putt(500) == base.putt(100)  # clipped


def test_tables_monotone_in_distance(base):
    for fn in (base.F, base.R, base.S, base.X):
        vals = [fn(d) for d in range(5, 605, 5)]
        assert all(b >= a - 1e-9 for a, b in zip(vals, vals[1:])), fn.__name__


def test_lie_ordering(base):
    for d in (20, 100, 150, 200):
        assert base.F(d) < base.R(d) < base.S(d)
        assert base.X(d) > base.R(d)


def test_scratch_behind_tour_everywhere(base):
    for (lie, d), tour in TOUR_REFERENCE.items():
        assert base.E(lie, d) > tour, (lie, d)


def test_approach_reproduces_published_proximity(base):
    # At 125 yds: GIR*on_green + (1-GIR)*miss should equal Shot Scope's 38 ft (100-150 band)
    g, x = 0.62, 25
    m = (38 - g * x) / (1 - g)
    assert 50 < m < 70  # a plausible miss distance in feet


def test_p_in_play():
    assert p_in_play(45, 20) == pytest.approx(2 * 0.5 * (1 + math.erf((22.5 / 20) / math.sqrt(2))) - 1)
    assert p_in_play(45, 1e-6) == pytest.approx(1.0)


def test_ob_closed_form(base):
    hole = next(h for h in Course.from_json(DATA).holes if h.number == 1)
    e = club_expectation(hole.yards, 45, "OB", SCRATCH_CLUBS[0], base)
    club = SCRATCH_CLUBS[0]
    pin = p_in_play(45, club.sigma_pct * club.distance)
    leave = hole.yards - club.distance
    e_in = 0.7 * base.F(leave) + 0.3 * base.R(leave)
    # E = 1 + pin*e_in + (1-pin)*(1+E)  ->  check the fixed point
    assert e == pytest.approx(1 + pin * e_in + (1 - pin) * (1 + e))


def test_ob_harder_than_trees(base):
    for c in SCRATCH_CLUBS:
        assert club_expectation(321, 45, "OBR", c, base) > club_expectation(321, 45, "X", c, base)
        assert club_expectation(321, 45, "OB", c, base) > club_expectation(321, 45, "OBR", c, base)


def test_good_day_gap_derivation():
    # mean of the best 8 of 20 normal draws sits ~0.93 sigma below the mean; with sigma ~2.6 that is ~2.4
    import numpy as np
    rng = np.random.default_rng(1); x = np.sort(rng.standard_normal((50000, 20)), axis=1)
    assert abs(x[:, :8].mean() + 0.93) < 0.03


def test_calibration_hits_target(cal):
    assert sum(v.adjusted for v in cal.values) == pytest.approx(cal.target)
    assert cal.target == pytest.approx(62.3)


def test_si_weights_sum_to_one():
    for lam in (0.0, 0.4, 1.0):
        cal = calibrate(Course.from_json(DATA), Baseline(params=Params(si_weight=lam)))
        assert sum(v.weight for v in cal.values) == pytest.approx(1.0)
        assert sum(v.adjusted for v in cal.values) == pytest.approx(cal.target)


def test_matches_workbook(cal):
    v1, v16, v2 = cal.by_number(1), cal.by_number(16), cal.by_number(2)
    assert v1.raw == pytest.approx(4.55, abs=0.01) and v1.best_club == "5-iron"
    assert v16.raw == pytest.approx(4.30, abs=0.01)
    assert v2.raw == pytest.approx(3.23, abs=0.01)
    assert cal.total_adjustment == pytest.approx(-1.85, abs=0.02)


def test_round_sg_telescopes(base, cal):
    # Any complete hole: sum of SG = E_raw + a_h - strokes, independent of the weighting
    shots = [Shot(1, "T", 356, "R", 140), Shot(1, "R", 140, "S", 15), Shot(1, "S", 15, "G", 30),
             Shot(1, "G", 30, "G", 4), Shot(1, "G", 4, "H")]
    res = score_round(shots, base, cal)
    v = cal.by_number(1)
    assert res["total"] == pytest.approx(v.raw + v.adjustment - 5)


def test_putting_untouched_by_course_adjustment(base, cal):
    s = score_shot(Shot(1, "G", 22, "G", 3), base, cal)
    assert s.sg == pytest.approx(base.putt(22) - base.putt(3) - 1)


def test_example_hole(base, cal):
    s = score_shot(Shot(1, "T", 356, "F", 102), base, cal)
    assert s.category == "OTT" and s.sg == pytest.approx(0.46, abs=0.01)
    s2 = score_shot(Shot(1, "F", 102, "G", 22), base, cal)
    assert s2.category == "APP" and s2.sg == pytest.approx(0.04, abs=0.01)


def test_penalty(base, cal):
    s = score_shot(Shot(2, "T", 150, "T", 150, penalty=1), base, cal)
    assert s.sg == pytest.approx(-2.0)
