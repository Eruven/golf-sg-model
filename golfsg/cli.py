"""Command line: show a calibrated course, or score a shot log CSV.

    python -m golfsg.cli data/fox_creek.json
    python -m golfsg.cli data/fox_creek.json --shots my_round.csv

Shot CSV columns: hole,start_lie,start_dist,end_lie,end_dist,penalty[,note]
"""
from __future__ import annotations

import argparse
import csv

from .baseline import Baseline
from .course import Course, calibrate
from .params import TOUR_REFERENCE
from .scoring import Shot, score_round


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Scratch-calibrated strokes gained")
    ap.add_argument("course", help="course JSON (see data/fox_creek.json)")
    ap.add_argument("--shots", help="CSV shot log to score")
    ap.add_argument("--tour-check", action="store_true", help="print scratch vs tour reference values")
    a = ap.parse_args(argv)

    base = Baseline()
    course = Course.from_json(a.course)
    cal = calibrate(course, base)

    print(f"{course.name} — {course.tees} tees, par {course.par}, CR {course.course_rating}")
    print(f"{'Hole':>4} {'Par':>3} {'Yds':>4} {'Trouble':>7} {'Raw E':>6} {'Adj':>6} {'E':>6}  Best club")
    for v in cal.values:
        h = v.hole
        print(f"{h.number:>4} {h.par:>3} {h.yards:>4.0f} {(h.trouble if h.par > 3 else '-'):>7} "
              f"{v.raw:>6.2f} {v.adjustment:>6.2f} {v.adjusted:>6.2f}  {v.best_club or ''}")
    print(f"raw total {sum(v.raw for v in cal.values):.2f}, target {cal.target:.2f}, "
          f"course adjustment {cal.total_adjustment:+.2f}")

    if a.tour_check:
        print("\nScratch minus tour (approx. Broadie values):")
        for (lie, d), tour in TOUR_REFERENCE.items():
            print(f"  {lie} {d:>4}  scratch {base.E(lie, d):.2f}  tour {tour:.2f}  diff {base.E(lie, d) - tour:+.2f}")

    if a.shots:
        with open(a.shots, newline="") as f:
            rows = list(csv.DictReader(f))
        shots = [Shot(int(r["hole"]), r["start_lie"], float(r["start_dist"]), r["end_lie"],
                      float(r["end_dist"]) if r.get("end_dist") not in (None, "") else None,
                      int(r.get("penalty") or 0), r.get("note", "")) for r in rows]
        res = score_round(shots, base, cal)
        print(f"\n{'Hole':>4} {'Cat':>4} {'From':>10} {'To':>10} {'E0':>5} {'E1':>5} {'SG':>6}")
        for s in res["shots"]:
            sh = s.shot
            print(f"{sh.hole:>4} {s.category:>4} {sh.start_lie + ' ' + str(sh.start_dist):>10} "
                  f"{sh.end_lie + ' ' + str(sh.end_dist or ''):>10} {s.e_start:>5.2f} {s.e_end:>5.2f} {s.sg:>+6.2f}")
        print("\nBy category: " + ", ".join(f"{k} {v:+.2f}" for k, v in res["by_category"].items()))
        print(f"Total {res['total']:+.2f} over {res['holes']} holes, {res['strokes']} strokes")


if __name__ == "__main__":
    main()
