
# ProofTrail AI — Benchmark Specification

Version: 1.0
Status: Initial test specification
Scope: Synthetic security-event correlation

## 1. Purpose

This specification defines expected verifier outcomes for controlled
security-event evidence scenarios.

It is the reference used to review test outcomes. It does not claim
that temporal ordering proves causality or that synthetic results
represent real-world SOC performance.

## 2. Verdicts

- supported: The available evidence satisfies the implemented,
  explicitly permitted checks and timing constraints.
- contradicted: The evidence violates a required condition.
- unknown: Evidence is missing, ambiguous, conflicting, or outside
  the verifier's supported relationship types.

A supported verdict is not proof of causality.

## 3. Expected outcomes

### Evidence completeness

- If a required source or target event is missing, return unknown.
- Report only evidence event IDs that are actually present and
  relevant to the evaluated claim.

### Duplicate event IDs

- If records with the same event ID conflict, return unknown.
- Do not silently choose one conflicting record as authoritative.

### Relationship type

- If the requested relationship is unsupported, return unknown.
- In particular, the baseline must not assert that one event
  caused another merely because their timestamps are compatible.

### Host consistency

- If a referenced event's host conflicts with the claimed host,
  return contradicted.
- Host agreement alone does not establish causality.

### Clock uncertainty and time windows

Let:
- source time be S
- target time be T
- source uncertainty be Us
- target uncertainty be Ut
- maximum permitted gap be M

The possible time-gap interval is:

    lower bound = (T - S) - (Us + Ut)
    upper bound = (T - S) + (Us + Ut)

Expected outcomes:

- If either uncertainty value is negative, return unknown.
- If the upper bound is less than zero, return contradicted:
  the target is earlier even after accounting for uncertainty.
- If the lower bound is less than zero but the upper bound is
  non-negative, return unknown because ordering is ambiguous.
- If the lower bound exceeds M, return contradicted because the
  gap is definitely too large.
- If the lower bound is within M but the upper bound exceeds M,
  return unknown because the permitted time window is ambiguous.
- Otherwise, return supported.

All boundaries are inclusive where the rule says the gap is
within M. These checks establish temporal consistency only.

## 4. Test independence

Expected outcomes must be specified directly in test cases or
derived from this written specification.

Tests must not call the verifier to calculate their expected
verdicts.

The stress test is useful for broad consistency checking, but
it is not independent validation if its expected results are
computed using the same decision rules as the verifier.

## 5. Limitations

This is a small, manually reviewed specification for a synthetic
baseline. It does not cover every possible input, real-world event
semantics, source reliability, identity resolution, or causal proof.

Changes to the specification should be reviewed separately from
changes to the verifier implementation.
