from evidently.core import BaseResult
from evidently.calculations.stattests.registry import StatTestResult


class StatResult(BaseResult):
    drift_score: float
    drifted: bool
    actual_threshold: float

def map_into_stat_results(data: StatTestResult) -> StatResult:
    return StatResult(
        drift_score = data.drift_score,
        drifted = data.drifted,
        actual_threshold = data.actual_threshold
    )