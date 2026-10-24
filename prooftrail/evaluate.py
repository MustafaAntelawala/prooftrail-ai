"""Evaluation metrics for three-way verdicts."""
from collections import Counter


def evaluate_rows(rows: list[dict]) -> dict:
    labels = ("supported", "contradicted", "unknown")
    counts = Counter((r["expected_verdict"], r["actual_verdict"]) for r in rows)
    correct = sum(counts[(label, label)] for label in labels)
    total = len(rows)
    # Treat supported as acceptance; all other outcomes are non-acceptance.
    expected_positive = sum(r["expected_verdict"] == "supported" for r in rows)
    predicted_positive = sum(r["actual_verdict"] == "supported" for r in rows)
    true_positive = sum(
        r["expected_verdict"] == "supported" and r["actual_verdict"] == "supported"
        for r in rows
    )
    false_accept = sum(
        r["expected_verdict"] != "supported" and r["actual_verdict"] == "supported"
        for r in rows
    )
    false_reject = sum(
        r["expected_verdict"] == "supported" and r["actual_verdict"] != "supported"
        for r in rows
    )
    precision = true_positive / predicted_positive if predicted_positive else 0.0
    recall = true_positive / expected_positive if expected_positive else 0.0
    return {
        "total_cases": total,
        "accuracy": correct / total if total else 0.0,
        "supported_precision": precision,
        "supported_recall": recall,
        "false_acceptance_count": false_accept,
        "false_rejection_count": false_reject,
        "confusion_matrix": {
            expected: {actual: counts[(expected, actual)] for actual in labels}
            for expected in labels
        },
    }
