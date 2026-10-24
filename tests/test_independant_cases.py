
"""Independent expected-outcome tests for ProofTrail AI.

Expected verdicts are explicitly specified per test case rather
than calculated using the verifier's temporal decision logic.
"""

import pytest

from prooftrail.models import Event, Claim, Scenario
from prooftrail.verifier import verify


def make_event(
    event_id,
    timestamp,
    host="HOST-A",
    uncertainty=0,
):
    return Event(
        event_id=event_id,
        timestamp=timestamp,
        host=host,
        event_type="security_event",
        user="alice",
        clock_uncertainty_minutes=uncertainty,
    )


def make_scenario(events, relation="same_host_temporal_sequence",
                  claimed_host="HOST-A", max_gap=10):
    claim = Claim(
        claim_id="C1",
        source_event_id="E1",
        target_event_id="E2",
        relation=relation,
        claimed_host=claimed_host,
        max_gap_minutes=max_gap,
    )

    return Scenario(
        scenario_id="independent_test",
        events=tuple(events),
        claim=claim,
        expected_verdict="not_used_by_test",
        mutation="independent_test",
    )


@pytest.mark.parametrize(
    ("target_time", "expected"),
    [
        (11, "supported"),       # Exactly at the 10-minute limit
        (12, "contradicted"),    # One minute beyond the limit
        (1, "supported"),        # Zero-minute gap
        (0, "contradicted"),     # Target precedes source
    ],
)
def test_explicit_time_boundaries(target_time, expected):
    scenario = make_scenario([
        make_event("E1", 1),
        make_event("E2", target_time),
    ])

    assert verify(scenario)["verdict"] == expected


def test_host_mismatch_is_contradicted():
    scenario = make_scenario([
        make_event("E1", 1),
        make_event("E2", 4, host="HOST-B"),
    ])

    assert verify(scenario)["verdict"] == "contradicted"


def test_missing_source_is_unknown():
    scenario = make_scenario([
        make_event("E2", 4),
    ])

    result = verify(scenario)

    assert result["verdict"] == "unknown"
    assert result["evidence_event_ids"] == ["E2"]


def test_unsupported_causal_relationship_is_unknown():
    scenario = make_scenario(
        [
            make_event("E1", 1),
            make_event("E2", 4),
        ],
        relation="caused_by",
    )

    assert verify(scenario)["verdict"] == "unknown"


def test_conflicting_duplicate_event_id_is_unknown():
    scenario = make_scenario([
        make_event("E1", 1),
        make_event("E2", 4),
        make_event("E2", 4, host="HOST-B"),
    ])

    result = verify(scenario)

    assert result["verdict"] == "unknown"
    assert result["evidence_event_ids"] == ["E2"]


def test_ordering_ambiguity_with_clock_uncertainty_is_unknown():
    scenario = make_scenario([
        make_event("E1", 10, uncertainty=2),
        make_event("E2", 9, uncertainty=2),
    ])

    assert verify(scenario)["verdict"] == "unknown"


def test_reversal_beyond_clock_uncertainty_is_contradicted():
    scenario = make_scenario([
        make_event("E1", 10, uncertainty=2),
        make_event("E2", 5, uncertainty=2),
    ])

    assert verify(scenario)["verdict"] == "contradicted"
