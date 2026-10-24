from dataclasses import replace
from prooftrail.mutations import build_benchmark
from prooftrail.verifier import verify
from prooftrail.evaluate import evaluate_rows


def test_expected_verdicts_for_starter_cases():
    for scenario in build_benchmark():
        assert verify(scenario)["verdict"] == scenario.expected_verdict, scenario.scenario_id


#def test_verifier_does_not_claim_causality():
    #scenario = build_benchmark()[0]
    #assert "causality is not proven" in verify(scenario)["reason"]

def test_verifier_does_not_claim_causality():
    scenario = build_benchmark()[0]
    reason = verify(scenario)["reason"].lower()
    assert "does not establish causality" in reason


def test_conflicting_duplicate_event_id_returns_unknown():
    scenario = build_benchmark()[0]
    conflicting = replace(scenario.events[1], host="HOST-Z")
    altered = replace(scenario, events=scenario.events + (conflicting,))
    assert verify(altered)["verdict"] == "unknown"


def test_metrics_count_false_acceptance():
    rows = [
        {"expected_verdict": "contradicted", "actual_verdict": "supported"},
        {"expected_verdict": "supported", "actual_verdict": "supported"},
        {"expected_verdict": "unknown", "actual_verdict": "unknown"},
    ]
    metrics = evaluate_rows(rows)
    assert metrics["false_acceptance_count"] == 1
    assert metrics["total_cases"] == 3


def test_small_timestamp_reversal_within_uncertainty_is_unknown():
    scenario = build_benchmark()[0]
    source, target = scenario.events

    source = replace(source, clock_uncertainty_minutes=1)
    target = replace(target, timestamp=0, clock_uncertainty_minutes=1)

    scenario = replace(scenario, events=(source, target))

    assert verify(scenario)["verdict"] == "unknown"


def test_timestamp_reversal_beyond_uncertainty_is_contradicted():
    scenario = build_benchmark()[0]
    source, target = scenario.events

    source = replace(source, clock_uncertainty_minutes=1)
    target = replace(
        target,
        timestamp=-5,
        clock_uncertainty_minutes=1,
    )

    scenario = replace(scenario, events=(source, target))

    assert verify(scenario)["verdict"] == "contradicted"


def test_time_window_overlap_with_uncertainty_is_unknown():
    scenario = build_benchmark()[0]
    source, target = scenario.events

    source = replace(source, clock_uncertainty_minutes=1)
    target = replace(
        target,
        timestamp=9,
        clock_uncertainty_minutes=2,
    )

    scenario = replace(scenario, events=(source, target))

    assert verify(scenario)["verdict"] == "unknown"
