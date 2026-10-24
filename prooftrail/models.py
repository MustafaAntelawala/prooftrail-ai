"""Small, explicit data models for the ProofTrail MVP."""
from dataclasses import dataclass, asdict
from typing import Optional



@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp: int
    host: str
    event_type: str
    user: Optional[str] = None
    clock_uncertainty_minutes: int = 0

    def to_dict(self):
        return asdict(self)



@dataclass(frozen=True)
class Claim:
    claim_id: str
    source_event_id: str
    target_event_id: str
    relation: str
    claimed_host: str
    max_gap_minutes: int = 10

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    events: tuple[Event, ...]
    claim: Claim
    expected_verdict: str  # supported, contradicted, unknown
    mutation: str = "none"

    def to_dict(self):
        return {
            "scenario_id": self.scenario_id,
            "events": [e.to_dict() for e in self.events],
            "claim": self.claim.to_dict(),
            "expected_verdict": self.expected_verdict,
            "mutation": self.mutation,
        }
