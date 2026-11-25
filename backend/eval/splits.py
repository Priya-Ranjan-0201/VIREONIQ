"""
Entity-Level and Temporal Data Splitting with Strict Leakage Guards.

Implements:
1. Entity-disjoint train/validation/test splitting (by candidate ID and job ID).
2. Strict temporal-order splitting (preventing future data contamination).
3. Automated train/test leakage verification assertions.
"""

from typing import Any, Dict, List, Set, Tuple


class DataLeakageError(ValueError):
    """Raised when an entity or document overlaps between train and evaluation sets."""
    pass


def create_entity_split(
    records: List[Dict[str, Any]],
    entity_key: str = "candidate_id",
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Partitions records into train, validation, and test splits strictly by unique
    entity IDs, ensuring zero candidate or job identity overlap.
    """
    unique_entities = sorted(list({str(r[entity_key]) for r in records if entity_key in r}))
    total_entities = len(unique_entities)
    if total_entities == 0:
        return [], [], []

    train_cutoff = int(total_entities * train_ratio)
    val_cutoff = int(total_entities * (train_ratio + val_ratio))

    train_entities = set(unique_entities[:train_cutoff])
    val_entities = set(unique_entities[train_cutoff:val_cutoff])
    test_entities = set(unique_entities[val_cutoff:])

    train_set = [r for r in records if str(r.get(entity_key)) in train_entities]
    val_set = [r for r in records if str(r.get(entity_key)) in val_entities]
    test_set = [r for r in records if str(r.get(entity_key)) in test_entities]

    # Sanity check leakage immediately
    check_data_leakage(train_set, test_set, entity_key=entity_key)
    if val_set:
        check_data_leakage(train_set, val_set, entity_key=entity_key)
        check_data_leakage(val_set, test_set, entity_key=entity_key)

    return train_set, val_set, test_set


def create_temporal_split(
    records: List[Dict[str, Any]],
    timestamp_key: str = "created_at",
    split_ratio: float = 0.8,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Splits records chronologically to prevent temporal lookahead leakage.
    """
    sorted_records = sorted(records, key=lambda x: str(x.get(timestamp_key, "")))
    cutoff = max(1, int(round(len(sorted_records) * split_ratio)))
    return sorted_records[:cutoff], sorted_records[cutoff:]


def check_data_leakage(
    train_set: List[Dict[str, Any]],
    eval_set: List[Dict[str, Any]],
    entity_key: str = "candidate_id",
) -> None:
    """
    Verifies that zero entities overlap between train and evaluation sets.
    Raises DataLeakageError if leakage is detected.
    """
    train_ids: Set[str] = {str(r[entity_key]) for r in train_set if entity_key in r}
    eval_ids: Set[str] = {str(r[entity_key]) for r in eval_set if entity_key in r}

    overlap = train_ids.intersection(eval_ids)
    if overlap:
        sample = sorted(list(overlap))[:5]
        raise DataLeakageError(
            f"Data leakage detected! {len(overlap)} entities overlap between sets. "
            f"Overlapping IDs: {sample}"
        )
