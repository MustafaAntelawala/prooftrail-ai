
"""Command-line runner for the ProofTrail benchmark."""

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .mutations import build_benchmark
from .verifier import verify
from .evaluate import evaluate_rows


def sha256_json(data: object) -> str:
    """Return a stable SHA-256 fingerprint of JSON-serializable data."""
    serialized = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def run(output_path: str) -> dict:
    # Build the benchmark once so its metadata and results use the same inputs.
    scenarios = build_benchmark()

    # Fingerprint the complete, ordered benchmark input.
    benchmark_inputs = [
        scenario.to_dict()
        for scenario in scenarios
    ]
    benchmark_input_sha256 = sha256_json(benchmark_inputs)

    rows = []

    for scenario, scenario_input in zip(scenarios, benchmark_inputs):
        result = verify(scenario)

        rows.append({
            "scenario_id": scenario.scenario_id,
            "mutation": scenario.mutation,
            "expected_verdict": scenario.expected_verdict,
            "actual_verdict": result["verdict"],
            "correct": scenario.expected_verdict == result["verdict"],
            "reason": result["reason"],
            "evidence_event_ids": result["evidence_event_ids"],
            "input_sha256": sha256_json(scenario_input),
        })

    report = {
        "project": "ProofTrail AI",
        "version": __version__,
        "report_schema_version": 2,
        "benchmark_type": "synthetic_demo",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python_version": sys.version,
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "reproducibility": {
            "scenario_count": len(scenarios),
            "benchmark_input_sha256": benchmark_input_sha256,
            "hash_algorithm": "SHA-256",
            "serialization": (
                "JSON with sorted keys, compact separators, UTF-8 encoding"
            ),
        },
        "test_status": {
            "status": "not_run_by_benchmark",
            "note": (
                "The benchmark runner does not execute the test suite. "
                "Run pytest separately to validate tests."
            ),
        },
        "warning": (
            "Synthetic toy benchmark; metrics do not represent "
            "real-world SOC performance or establish causality."
        ),
        "metrics": evaluate_rows(rows),
        "cases": rows,
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Run the ProofTrail synthetic benchmark."
    )
    parser.add_argument(
        "--output",
        default="results/baseline.json",
        help="Path where the JSON benchmark report will be written.",
    )
    args = parser.parse_args()

    report = run(args.output)

    print(json.dumps(report["metrics"], indent=2))
    print("\nReproducibility metadata:")
    print(
        json.dumps(
            report["reproducibility"],
            indent=2,
        )
    )
    print(f"\nReport written to: {args.output}")


if __name__ == "__main__":
    main()
