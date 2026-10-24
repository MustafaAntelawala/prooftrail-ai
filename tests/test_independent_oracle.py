
"""Additional expected-outcome tests for ProofTrail AI.

Expected outcomes are specified directly from the documented policy.
These tests do not call the verifier to calculate their expected verdicts.
"""

from prooftrail.models import Event, Claim, Scenario
from prooftrail.verifier import verify


def make_event(event_id, timestamp, host="HOST-A", uncertainty=0):
    return Event(
        event_id=event_id,
        timestamp=timestamp,
        host=host,
        event_type="security_event",
        user="alice",
        clock_uncertainty_minutes=uncertainty,
    )


def make_scenario(events, max_gap=10, claimed_host="HOST-A"):
    return Scenario(
        scenario_id="independent_oracle_case",
        events=tuple(events),
        claim=Claim(
            claim_id="C1",
            source_event_id="E1",
            target_event_id="E2",
            relation="same_host_temporal_sequence",
            claimed_host=claimed_host,
            max_gap_minutes=max_gap,
        ),
        expected_verdict="not_used_by_test",
        mutation="independent_oracle",
    )


def test_target_missing_returns_unknown():
    scenario = make_scenario([
        make_event("E1", 1),
    ])

    assert verify(scenario)["verdict"] == "unknown"


def test_gap_at_limit_with_clock_uncertainty_is_unknown():
    # The nominal gap is 10 minutes, but each clock has 1 minute
    # of uncertainty, so the actual gap cannot be bounded to 10.
    scenario = make_scenario([
        make_event("E1", 0, uncertainty=1),
        make_event("E2", 10, uncertainty=1),
    ])

    assert verify(scenario)["verdict"] == "unknown"


def test_gap_clearly_exceeds_limit_despite_uncertainty():
    # Even allowing 1 minute of uncertainty per clock, the minimum
    # possible gap is 13 minutes, beyond the 10-minute limit.
    scenario = make_scenario([
        make_event("E1", 0, uncertainty=1),
        make_event("E2", 15, uncertainty=1),
    ])

    assert verify(scenario)["verdict"] == "contradicted"


def test_negative_clock_uncertainty_returns_unknown():
    scenario = make_scenario([
        make_event("E1", 0, uncertainty=-1),
        make_event("E2", 5),
    ])

    assert verify(scenario)["verdict"] == "unknown"


def test_claimed_host_mismatch_returns_contradicted():
    scenario = make_scenario(
        [
            make_event("E1", 0),
            make_event("E2", 5),
        ],
        claimed_host="HOST-B",
    )

    assert verify(scenario)["verdict"] == "contradicted"


def test_exact_maximum_gap_without_uncertainty_is_supported():
    scenario = make_scenario([
        make_event("E1", 0),
        make_event("E2", 10),
    ])

    assert verify(scenario)["verdict"] == "supported"


def test_target_before_source_beyond_uncertainty_is_contradicted():
    scenario = make_scenario([
        make_event("E1", 10, uncertainty=1),
        make_event("E2", 7, uncertainty=1),
    ])

    assert verify(scenario)["verdict"] == "contradicted"


def test_gap_within_limit_but_uncertainty_crosses_limit_is_unknown():
    scenario = make_scenario([
        make_event("E1", 0, uncertainty=1),
        make_event("E2", 9, uncertainty=1),
    ])

    assert verify(scenario)["verdict"] == "unknown"
