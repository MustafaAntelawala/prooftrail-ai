import json
from pathlib import Path

import pandas as pd
import streamlit as st

from prooftrail.cli import run as run_benchmark

st.set_page_config(
    page_title="ProofTrail AI",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ ProofTrail AI")
st.subheader("Security Event Correlation — Robustness Benchmark")
st.caption(
    "Test how a deterministic verifier handles corrupted, missing, "
    "duplicated, or contradictory security-event evidence."
)

st.warning(
    "Research prototype: results use synthetic scenarios and do not "
    "demonstrate real-world SOC accuracy or prove causality."
)

# Run the canonical benchmark only when requested.
st.subheader("Benchmark execution")

if st.button("Run benchmark", type="primary"):
    try:
        with st.spinner("Running benchmark..."):
            report = run_benchmark(
                str(Path("results") / "dashboard_report.json")
            )
        st.session_state["prooftrail_report"] = report
        st.success("Benchmark completed.")
    except Exception as exc:
        st.error(f"Benchmark failed: {exc}")

report = st.session_state.get("prooftrail_report")

if report is None:
    st.info("Click Run benchmark to generate results.")
    st.stop()

# Build dashboard rows from the canonical CLI report.
rows = []

for case in report["cases"]:
    rows.append({
        "Scenario": case["scenario_id"],
        "Mutation": case["mutation"],
        "Expected": case["expected_verdict"],
        "Actual": case["actual_verdict"],
        "Match": case["correct"],
        "Reason": case["reason"],
        "Evidence IDs": ", ".join(
            map(str, case["evidence_event_ids"])
        ),
        "SHA-256": case["input_sha256"],
    })

df = pd.DataFrame(rows)



# Read cases from the canonical CLI report
rows = []

for case in report["cases"]:
    rows.append({
        "Scenario": case["scenario_id"],
        "Mutation": case["mutation"],
        "Expected": case["expected_verdict"],
        "Actual": case["actual_verdict"],
        "Match": case["correct"],
        "Reason": case["reason"],
        "Evidence IDs": ", ".join(
            map(str, case["evidence_event_ids"])
        ),
        "SHA-256": case["input_sha256"],
    })

df = pd.DataFrame(rows)

# Summary
total = len(df)
matches = int(df["Match"].sum())
mismatches = total - matches
unknown_count = int(
    df["Actual"].str.lower().eq("unknown").sum()
)




col1, col2, col3, col4 = st.columns(4)
col1.metric("Total scenarios", total)
col2.metric("Expected / actual match", f"{matches}/{total}")
col3.metric("Mismatches", mismatches)
col4.metric("Unknown verdicts", unknown_count)


st.divider()
st.subheader("Benchmark Analytics")

# Verdict distribution
st.markdown("### Verdict distribution")
verdict_counts = (
    df["Actual"]
    .value_counts()
    .rename_axis("Verdict")
    .reset_index(name="Cases")
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.caption("Actual verifier verdicts")
    st.bar_chart(
        verdict_counts.set_index("Verdict"),
        y="Cases",
    )

with chart_col2:
    st.caption("Expected vs actual verdicts")
    comparison = pd.crosstab(
        df["Expected"],
        df["Actual"],
    )
    st.dataframe(
        comparison,
        use_container_width=True,
    )

# Mutation-level analysis
st.markdown("### Results by mutation")
mutation_summary = (
    df.groupby("Mutation", dropna=False)
    .agg(
        Cases=("Scenario", "count"),
        Matches=("Match", "sum"),
    )
    .reset_index()
)
mutation_summary["Mismatches"] = (
    mutation_summary["Cases"] - mutation_summary["Matches"]
)
mutation_summary["Agreement (%)"] = (
    100 * mutation_summary["Matches"] / mutation_summary["Cases"]
).round(1)

st.dataframe(
    mutation_summary,
    use_container_width=True,
    hide_index=True,
)

st.bar_chart(
    mutation_summary.set_index("Mutation")[
        ["Matches", "Mismatches"]
    ],
)

st.divider()
st.subheader("Explore benchmark cases")

# Filters
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    verdict_options = ["All"] + sorted(df["Actual"].unique().tolist())
    selected_verdict = st.selectbox(
        "Actual verdict",
        verdict_options,
    )

with filter_col2:
    mutation_options = ["All"] + sorted(
        df["Mutation"].astype(str).unique().tolist()
    )
    selected_mutation = st.selectbox(
        "Mutation type",
        mutation_options,
    )

with filter_col3:
    agreement_options = ["All", "Match", "Mismatch"]
    selected_agreement = st.selectbox(
        "Expected vs actual",
        agreement_options,
    )

filtered = df.copy()

if selected_verdict != "All":
    filtered = filtered[filtered["Actual"] == selected_verdict]

if selected_mutation != "All":
    filtered = filtered[
        filtered["Mutation"].astype(str) == selected_mutation
    ]

if selected_agreement == "Match":
    filtered = filtered[filtered["Match"]]
elif selected_agreement == "Mismatch":
    filtered = filtered[~filtered["Match"]]

st.caption(f"Showing {len(filtered)} of {len(df)} scenarios")

st.dataframe(
    filtered[
        [
            "Scenario",
            "Mutation",
            "Expected",
            "Actual",
            "Match",
            "Reason",
            "Evidence IDs",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

# Individual scenario details
st.markdown("### Scenario details")

available_scenarios = filtered["Scenario"].tolist()

if available_scenarios:
    selected_scenario = st.selectbox(
        "Select a scenario",
        available_scenarios,
    )

    selected_row = filtered[
        filtered["Scenario"] == selected_scenario
    ].iloc[0]

    st.write("**Mutation:**", selected_row["Mutation"])
    st.write("**Expected verdict:**", selected_row["Expected"])
    st.write("**Actual verdict:**", selected_row["Actual"])
    st.write("**Agreement:**", "Match" if selected_row["Match"] else "Mismatch")
    st.write("**Verifier reason:**", selected_row["Reason"])
    st.write("**Evidence IDs:**", selected_row["Evidence IDs"] or "None")
    st.write("**Scenario SHA-256:**")
    st.code(selected_row["SHA-256"], language="text")
else:
    st.info("No scenarios match the selected filters.")

# JSON export
# Export the canonical report generated by the CLI.
st.divider()
st.subheader("Export results")

st.write("**Report version:**", report["version"])
st.write("**Generated at (UTC):**", report["generated_at_utc"])
st.write("**Scenarios:**", report["reproducibility"]["scenario_count"])
st.write("**SHA-256:**")
st.code(
    report["reproducibility"]["benchmark_input_sha256"],
    language="text",
)

st.caption(
    "Test status: "
    + report["test_status"]["status"]
    + ". "
    + report["test_status"]["note"]
)

st.download_button(
    label="Download canonical benchmark report (JSON)",
    data=json.dumps(report, indent=2, ensure_ascii=False),
    file_name="prooftrail_benchmark_report.json",
    mime="application/json",
)

st.caption(
    "ProofTrail AI | Deterministic baseline | Synthetic test data only"
)