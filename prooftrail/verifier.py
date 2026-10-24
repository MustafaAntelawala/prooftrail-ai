
"""Deterministic verifier for security-event relationships.

This checks configured temporal and host invariants.
It does not establish real-world causality.
"""
from .models import Scenario


def verify(scenario: Scenario) -> dict:
    by_id = {}

    # Conflicting duplicate IDs make the evidence ambiguous.
    for event in scenario.events:
        if event.event_id in by_id and by_id[event.event_id] != event:
            return {
                "verdict": "unknown",
                "reason": f"Conflicting records share event_id={event.event_id}.",
                "evidence_event_ids": [event.event_id],
            }
        by_id[event.event_id] = event

    claim = scenario.claim

    # Only this relationship is supported by the baseline.
    if claim.relation != "same_host_temporal_sequence":
        return {
            "verdict": "unknown",
            "reason": (
                f"Relationship '{claim.relation}' is not validated "
                "by the deterministic baseline."
            ),
            "evidence_event_ids": [],
        }

    source = by_id.get(claim.source_event_id)
    target = by_id.get(claim.target_event_id)

    if source is None or target is None:
        return {
            "verdict": "unknown",
            "reason": "Required source or target event is missing.",
            "evidence_event_ids": [
                event_id
                for event_id in (
                    claim.source_event_id,
                    claim.target_event_id,
                )
                if event_id in by_id
            ],
        }

    evidence_ids = [source.event_id, target.event_id]

    if source.event_id == target.event_id:
        return {
            "verdict": "unknown",
            "reason": "Source and target refer to the same event.",
            "evidence_event_ids": evidence_ids,
        }

    if source.host != claim.claimed_host or target.host != claim.claimed_host:
        return {
            "verdict": "contradicted",
            "reason": "Referenced events do not match the claimed host.",
            "evidence_event_ids": evidence_ids,
        }

    if source.clock_uncertainty_minutes < 0 or target.clock_uncertainty_minutes < 0:
        return {
            "verdict": "unknown",
            "reason": "Clock uncertainty cannot be negative.",
            "evidence_event_ids": evidence_ids,
        }

    gap = target.timestamp - source.timestamp
    uncertainty = (
        source.clock_uncertainty_minutes
        + target.clock_uncertainty_minutes
    )

    # Earliest and latest plausible gaps given both clock uncertainties.
    min_gap = gap - uncertainty
    max_gap = gap + uncertainty

    if max_gap < 0:
        return {
            "verdict": "contradicted",
            "reason": "Target timestamp is earlier beyond the clock uncertainty window.",
            "evidence_event_ids": evidence_ids,
        }

    if min_gap < 0:
        return {
            "verdict": "unknown",
            "reason": "Event ordering is ambiguous because of clock uncertainty.",
            "evidence_event_ids": evidence_ids,
        }

    if min_gap > claim.max_gap_minutes:
        return {
            "verdict": "contradicted",
            "reason": "Event gap exceeds the configured time window.",
            "evidence_event_ids": evidence_ids,
        }

    if max_gap > claim.max_gap_minutes:
        return {
            "verdict": "unknown",
            "reason": "Clock uncertainty overlaps the time-window boundary.",
            "evidence_event_ids": evidence_ids,
        }

    return {
        "verdict": "supported",
        "reason": (
            "Host and time-window checks passed. "
            "This does not establish causality."
        ),
        "evidence_event_ids": evidence_ids,
    }
