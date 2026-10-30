import numpy as np
import pandas as pd
import pytest

from src.risk import LogisticPdModel, ModelError, RiskModel, RollRateModel


# ---- roll-rate model -------------------------------------------------------------------------------

def snapshot(case, month_end, dpd, balance, status="OPEN", account_status="OPEN"):
    return {"case_uuid": case, "snapshot_date": month_end, "dpd": dpd, "outstanding_balance": balance,
            "status": status, "account_status": account_status}


# three loans over three month-ends, chosen so the roll rates are easy to work out by hand:
#   a: current -> current -> 1-30        b: 1-30 -> current -> SETTLED        c: 90+ -> 90+ -> WRITTEN_OFF
SNAPSHOTS = [
    snapshot("a", "2026-01-31", 0, 100), snapshot("a", "2026-02-28", 0, 100), snapshot("a", "2026-03-31", 10, 100),
    snapshot("b", "2026-01-31", 20, 50), snapshot("b", "2026-02-28", 0, 40),
    snapshot("b", "2026-03-31", 0, 0, status="SETTLED", account_status="CLOSED"),
    snapshot("c", "2026-01-31", 120, 80), snapshot("c", "2026-02-28", 150, 80),
    snapshot("c", "2026-03-31", 150, 80, status="WRITTEN_OFF", account_status="CLOSED"),
]


@pytest.fixture
def roll_rates(policy):
    return RollRateModel(policy).fit(SNAPSHOTS)


def test_roll_rates_are_shares_of_balance(roll_rates):
    m = roll_rates.matrix
    # current: a stays (100), then a rolls to 1-30 (100), and b (40) settles -> 100 / 240 stays current
    assert m.loc["current", "current"] == pytest.approx(100 / 240)
    assert m.loc["current", "1-30"] == pytest.approx(100 / 240)
    assert m.loc["current", "SETTLED"] == pytest.approx(40 / 240)
    assert m.loc["1-30", "current"] == pytest.approx(1.0)
    assert m.loc["90+", "WRITTEN_OFF"] == pytest.approx(0.5)
    assert roll_rates.transitions == 6


def test_every_row_adds_up_and_closed_states_stay_closed(roll_rates):
    assert np.allclose(roll_rates.matrix.sum(axis=1), 1)
    assert roll_rates.matrix.loc["SETTLED", "SETTLED"] == 1
    assert roll_rates.matrix.loc["WRITTEN_OFF", "WRITTEN_OFF"] == 1
    # no history from 31-60, so it stays put rather than inventing a move
    assert roll_rates.matrix.loc["31-60", "31-60"] == 1


def test_until_ignores_later_month_ends(policy):
    early = RollRateModel(policy).fit(SNAPSHOTS, until="2026-02-28")
    assert early.transitions == 3
    assert early.matrix.loc["90+", "WRITTEN_OFF"] == 0


def test_projection_keeps_the_total_balance(roll_rates):
    start = pd.Series({"current": 1000.0, "90+": 500.0})
    projection = roll_rates.project(start, months=6)

    assert len(projection) == 7
    assert np.allclose(projection.sum(axis=1), 1500)
    assert projection.loc[0, "current"] == 1000
    assert projection["WRITTEN_OFF"].is_monotonic_increasing


def test_expected_write_offs_count_only_new_write_offs(roll_rates):
    start = pd.Series({"90+": 1000.0, "WRITTEN_OFF": 300.0})
    table = roll_rates.expected_write_offs(start, horizons=(1, 2))
    # half the 90+ balance is written off each month: 500 after one month, 750 after two
    assert table["written off (UGX)"].tolist() == [500, 750]
    assert table["share of open balance %"].tolist() == [50.0, 75.0]


def test_predict_pd_is_the_chance_of_being_written_off_within_the_horizon(policy):
    model = RollRateModel(policy, horizon=2).fit(SNAPSHOTS)
    pds = model.predict_pd(pd.DataFrame({"bucket": ["90+", "current", "WRITTEN_OFF"]}))
    assert pds.tolist() == pytest.approx([0.75, 0.0, 1.0])
    assert isinstance(model, RiskModel)


def test_roll_rate_errors(policy, roll_rates):
    with pytest.raises(ModelError, match="call fit"):
        RollRateModel(policy).project(pd.Series({"current": 1.0}))
    with pytest.raises(ModelError, match="months must be at least 1"):
        roll_rates.project(pd.Series({"current": 1.0}), months=0)
    with pytest.raises(ModelError, match="Unknown states"):
        roll_rates.project(pd.Series({"nowhere": 1.0}))
    with pytest.raises(ModelError, match="Unknown buckets"):
        roll_rates.predict_pd(pd.DataFrame({"bucket": ["nowhere"]}))
    with pytest.raises(ModelError, match="horizon must be at least 1"):
        RollRateModel(policy, horizon=0)
    with pytest.raises(ModelError, match="unknown final status"):
        RollRateModel(policy).fit(SNAPSHOTS + [snapshot("d", "2026-01-31", 0, 5, "LOST", "CLOSED")])
    with pytest.raises(ModelError, match="No month-to-month moves"):
        RollRateModel(policy).fit(SNAPSHOTS[:1])


def test_actual_path_follows_each_loan_with_its_starting_balance(roll_rates):
    path = roll_rates.actual_path(SNAPSHOTS, "2026-01-31", months=2)
    assert path.loc[0, "current"] == 100 and path.loc[0, "1-30"] == 50 and path.loc[0, "90+"] == 80
    assert path.loc[2, "1-30"] == 100 and path.loc[2, "SETTLED"] == 50 and path.loc[2, "WRITTEN_OFF"] == 80
    with pytest.raises(ModelError, match="Only 0 months"):
        roll_rates.actual_path(SNAPSHOTS, "2026-03-31", months=1)


# ---- logistic PD model -----------------------------------------------------------------------------

@pytest.fixture
def loans():
    """Loans where defaults come from high DPD, so a model has a clear signal to find."""
    rng = np.random.default_rng(7)
    dpd = rng.integers(0, 120, 400)
    return pd.DataFrame({"dpd": dpd, "income": rng.normal(1_000_000, 200_000, 400),
                         "product": rng.choice(["school", "business"], 400),
                         "defaulted": (dpd + rng.normal(0, 20, 400) > 90).astype(int)})


def test_logistic_model_learns_the_signal(loans):
    model = LogisticPdModel(["dpd", "income"], ["product"]).fit(loans)
    pds = model.predict_pd(loans)

    assert pds.between(0, 1).all() and pds.index.equals(loans.index)
    evaluation = model.evaluate(loans, bands=4)
    assert evaluation.auc > 0.9
    assert evaluation.bands["band"].tolist() == ["A", "B", "C", "D"]
    assert evaluation.bands["default_rate"].iloc[-1] > evaluation.bands["default_rate"].iloc[0]
    assert model.coefficients().loc[0, "feature"] == "dpd"


def test_logistic_model_errors(loans):
    model = LogisticPdModel(["dpd"], [])
    with pytest.raises(ModelError, match="call fit"):
        model.predict_pd(loans)
    with pytest.raises(ModelError, match="both defaults and non-defaults"):
        model.fit(loans.assign(defaulted=0))
    with pytest.raises(ModelError, match="Missing feature columns: dpd"):
        model.fit(loans.drop(columns="dpd"))


def test_save_and_load_round_trip(loans, tmp_path):
    model = LogisticPdModel(["dpd"], []).fit(loans)
    path = model.save(tmp_path / "models" / "pd.joblib")

    loaded = model.load(path)
    assert loaded.predict_pd(loans).equals(model.predict_pd(loans))
    with pytest.raises(ModelError, match="not found"):
        model.load(tmp_path / "missing.joblib")
    with pytest.raises(ModelError, match="call fit"):
        LogisticPdModel(["dpd"], []).save(tmp_path / "untrained.joblib")
