
"""Controlled telemetry mutations for synthetic benchmark scenarios."""
from dataclasses import replace

from .models import Claim, Event, Scenario


def make_base_scenario() -> Scenario:
    events = (
        Event("E1", 1, "HOST-A", "logon_success", "alice"),
        Event("E2", 4, "HOST-A", "suspicious_connection", "alice"),
    )
    claim = Claim(
        claim_id="C1",
        source_event_id="E1",
        target_event_id="E2",
        relation="same_host_temporal_sequence",
        claimed_host="HOST-A",
        max_gap_minutes=10,
    )
    return Scenario("base", events, claim, "supported", "none")


def build_benchmark() -> list[Scenario]:
    base = make_base_scenario()
    e1, e2 = base.events
    claim = base.claim

    cases = [base]

    cases.append(Scenario(
        "host_swap",
        (e1, replace(e2, host="HOST-B")),
        claim,
        "contradicted",
        "host_swap",
    ))

    cases.append(Scenario(
        "timestamp_skew",
        (e1, replace(e2, timestamp=30)),
        claim,
        "contradicted",
        "timestamp_skew",
    ))

    cases.append(Scenario(
        "missing_source",
        (e2,),
        claim,
        "unknown",
        "missing_event",
    ))

    cases.append(Scenario(
        "duplicate_target",
        (e1, e2, e2),
        claim,
        "supported",
        "duplicate_event",
    ))

    cases.append(Scenario(
        "reversed_time",
        (replace(e1, timestamp=9), replace(e2, timestamp=3)),
        claim,
        "contradicted",
        "contradictory_timestamps",
    ))

    # New: two corruptions applied to the same scenario.
    cases.append(Scenario(
        "combined_host_swap_and_time_skew",
        (e1, replace(e2, host="HOST-B", timestamp=30)),
        claim,
        "contradicted",
        "host_swap+timestamp_skew",
    ))

    # New: temporal proximity does not prove causation.
    causal_claim = replace(claim, relation="caused_by")
    cases.append(Scenario(
        "unsupported_causal_claim",
        (e1, e2),
        causal_claim,
        "unknown",
        "unsupported_relationship",
    ))

    # New: duplicate IDs with conflicting contents are ambiguous.
    conflicting_duplicate = replace(e2, host="HOST-Z")
    cases.append(Scenario(
        "conflicting_duplicate_id",
        (e1, e2, conflicting_duplicate),
        claim,
        "unknown",
        "conflicting_duplicate",
    ))

    return cases
