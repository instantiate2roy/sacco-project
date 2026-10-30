"""
End-to-end checks on the synthetic data in data/: the steps the notebook runs, checked against the policy.
"""
import numpy as np
import pandas as pd

from src.risk import LogisticPdModel


def test_data_files_load(pipeline):
    for name in ["customer", "case", "case_snapshot", "contact", "contact_history", "payment_history", "ptp",
                 "treatment_history", "savings_history", "security"]:
        assert pipeline.data[name]["rows"], name
    assert pipeline.kb["treatment_type"]["rows"]


def test_training_rows_only_have_known_outcomes(pipeline):
    rows = pipeline.rows
    assert set(rows["defaulted"].unique()) <= {0, 1}
    assert rows["observed_on"].max() < pd.Timestamp(pipeline.as_of)


def test_model_ranks_risk_on_months_it_did_not_see(pipeline):
    rows = pipeline.rows
    split = pd.Timestamp("2025-12-31")
    train, test = rows[rows["observed_on"] < split], rows[rows["observed_on"] >= split]
    model = LogisticPdModel(pipeline.model.numeric, pipeline.model.categorical).fit(train)
    assert model.evaluate(test).auc > 0.85


def test_every_loan_gets_a_bucket_tier_and_profile_that_follow_the_policy(pipeline):
    today, policy = pipeline.today, pipeline.policy
    assert len(today) and today["case_uuid"].is_unique
    assert (today["bucket"] == today["dpd"].map(policy.bucket_for)).all()
    assert (today["tier"] == today["pd"].map(policy.tier_for)).all()
    assert set(today["profile"]) <= {rule["name"] for rule in policy.profiles} | {policy.default_profile}


def test_proposed_treatments_come_from_the_matrix_or_its_fallbacks(pipeline):
    policy, today = pipeline.policy, pipeline.today.set_index("case_uuid")
    fallbacks = policy.fallback_treatments
    for action in pipeline.actions:
        loan = today.loc[action.case_uuid]
        assert loan["dpd"] > 0
        chain, treatment = [], policy.treatment_for(loan["profile"], loan["bucket"])
        while treatment and treatment not in chain:
            chain.append(treatment)
            treatment = fallbacks.get(treatment)
        assert action.treatment in chain


def test_every_decision_is_logged(pipeline):
    log = pipeline.log.to_frame()
    assert len(log) == len(pipeline.decisions)
    assert (log["status"] == "BLOCKED").sum() == (~pipeline.decisions["allowed"]).sum()
    assert set(log["status"]) <= {"SENT", "QUEUED", "REFERRED", "BLOCKED"}


def test_roll_rates_from_the_snapshots_add_up(pipeline):
    matrix = pipeline.roll_rates.matrix
    assert np.allclose(matrix.sum(axis=1), 1)
    start = pipeline.roll_rates.balances(pipeline.today)
    assert np.isclose(pipeline.roll_rates.project(start, 12).iloc[-1].sum(), start.sum())


def test_worklist_ranks_overdue_loans_by_expected_loss(pipeline):
    from src.display import Worklist

    worklist = Worklist(pipeline.portfolio, pipeline.as_of)
    frame = worklist.frame
    assert len(frame) == (pipeline.today["dpd"] > 0).sum() and (frame["dpd"] > 0).all()
    assert frame["expected_loss"].is_monotonic_decreasing
    assert frame["rank"].tolist() == list(range(1, len(frame) + 1))

    worklist.widget()
    tier = next(f for f in worklist.filters if f.column == "tier")
    tier.widget.value = "E"
    shown = worklist.matches()
    # the rank stays each loan's place in the whole worklist
    assert set(shown["tier"]) == {"E"} and shown["rank"].is_monotonic_increasing
    assert shown["rank"].tolist() == frame.loc[frame["tier"] == "E", "rank"].tolist()
