import json
from collections import defaultdict
from typing import List, Tuple, Optional

class TurningPoint:
    def __init__(self,
                 id: str,
                 name: str,
                 category: str,
                 uncertainty_types: list[str],
                 commitment_range: tuple[int, int],
                 repeatable: bool,
                 min_scenes_since_start: int,
                 notes: str = ""):
        self.id = id
        self.name = name
        self.category = category
        self.uncertainty_types = uncertainty_types
        self.commitment_range = tuple(commitment_range)
        self.repeatable = repeatable
        self.min_scenes_since_start = min_scenes_since_start
        self.notes = notes

    def fits_commitment(self, score: float) -> bool:
        lo, hi = self.commitment_range
        return lo <= score <= hi

def build_indexes(turning_points: list[TurningPoint]):
    idx = {
        "by_category": defaultdict(set),
        "by_uncertainty": defaultdict(set),
        "repeatable": set(),
        "one_time": set(),
        "by_id": {}
    }

    for tp in turning_points:
        tid = tp.id
        idx["by_id"][tid] = tp
        idx["by_category"][tp.category].add(tid)
        for u in tp.uncertainty_types:
            idx["by_uncertainty"][u].add(tid)
        if tp.repeatable:
            idx["repeatable"].add(tid)
        else:
            idx["one_time"].add(tid)

    return idx


def query_turning_points(indexes,
                         category=None,
                         uncertainty=None,
                         commitment=None,
                         commitment_trend=None,
                         repeatable=None,
                         scenes_since_start=None):

    # Start with all IDs
    candidates = set(indexes["by_id"].keys())

    if category:
        candidates &= indexes["by_category"][category]
    if uncertainty:
        candidates &= indexes["by_uncertainty"][uncertainty]
    if repeatable is True:
        candidates &= indexes["repeatable"]
    elif repeatable is False:
        candidates &= indexes["one_time"]

    results = []
    for tid in candidates:
        tp = indexes["by_id"][tid]
        
        # Commitment range check
        if commitment is not None and not tp.fits_commitment(commitment):
            continue

        # Time since relationship start
        if scenes_since_start is not None and scenes_since_start < tp.min_scenes_since_start:
            continue

        # Commitment trend check (example rule set)
        if commitment_trend:
            if commitment_trend == "improving" and tp.category in ["Transitions & Endings"]:
                continue
            if commitment_trend == "deteriorating" and tp.category in ["Bonding", "Deepening"]:
                continue

        results.append(tp)

    return results
