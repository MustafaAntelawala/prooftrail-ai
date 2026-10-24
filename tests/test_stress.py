
from dataclasses import replace

from prooftrail.mutations import make_base_scenario
from prooftrail.verifier import verify


def expected_verdict(gap, uncertainty, max_gap):
    """Independent oracle for the benchmark's temporal policy."""
    min_gap = gap - uncertainty
    max_possible_gap = gap + uncertainty

    if max_possible_gap < 0:
        return "contradicted"

    if min_gap < 0:
        return "unknown"

    if min_gap > max_gap:
        return "contradicted"

    if max_possible_gap > max_gap:
        return "unknown"

    return "supported"


def test_many_clock_uncertainty_combinations():
    base = make_base_scenario()
    source, target = base.events
    checked = 0

    for gap in range(-10, 21):
        for source_uncertainty in range(4):
            for target_uncertainty in range(4):
                uncertainty = source_uncertainty + target_uncertainty

                source_event = replace(
                    source,
                    timestamp=10,
                    clock_uncertainty_minutes=source_uncertainty,
                )
                target_event = replace(
                    target,
                    timestamp=10 + gap,
                    clock_uncertainty_minutes=target_uncertainty,
                )

                scenario = replace(
                    base,
                    events=(source_event, target_event),
                )

                expected = expected_verdict(
                    gap,
                    uncertainty,
                    scenario.claim.max_gap_minutes,
                )
                actual = verify(scenario)["verdict"]

                assert actual == expected, (
                    f"gap={gap}, uncertainty={uncertainty}: "
                    f"expected {expected}, got {actual}"
                )
                checked += 1

    assert checked == 496
