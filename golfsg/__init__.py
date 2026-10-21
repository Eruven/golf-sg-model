"""golfsg: scratch-calibrated, course-specific strokes gained."""
from .baseline import Baseline
from .course import Course, Hole, calibrate
from .params import SCRATCH_CLUBS, Club, Params, ScratchData
from .scoring import Shot, score_round, score_shot
from .tee import club_expectation, p_in_play, tee_model

__all__ = ["Baseline", "Course", "Hole", "calibrate", "SCRATCH_CLUBS", "Club", "Params", "ScratchData",
           "Shot", "score_round", "score_shot", "club_expectation", "p_in_play", "tee_model"]
__version__ = "0.1.0"
