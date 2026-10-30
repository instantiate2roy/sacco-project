import numpy as np
import pandas as pd

from ..policy import Policy
from .error import ModelError
from .risk_model import RiskModel


class RollRateModel(RiskModel):
    """
    A Markov chain of how loan balances move between delinquency buckets from one month-end to the next.

    Each month-end snapshot puts a loan in a state: one of the policy's buckets while it is open, or
    SETTLED or WRITTEN_OFF once it closes. The roll rates are the share of each bucket's balance found in
    each state a month later: how much cures, stays, rolls to a worse bucket, is paid off or is written
    off. SETTLED and WRITTEN_OFF are absorbing: a closed loan stays closed.

    A projection multiplies today's balance in each state by the roll-rate matrix once per month. It
    follows today's loans only: new lending isn't included, and repayments that don't close a loan aren't
    modelled, so it shows where today's balance ends up rather than the future size of the book.

    As a RiskModel, a loan's PD is the chance its bucket's balance is written off within `horizon` months.
    """

    name = "roll-rate model"
    closed_statuses = ["SETTLED", "WRITTEN_OFF"]

    def __init__(self, policy: Policy, horizon: int = 12):
        super().__init__(["bucket"])
        if horizon < 1:
            raise ModelError(f"horizon must be at least 1, not {horizon}")
        self.policy = policy
        self.horizon = horizon
        self.states = [bucket["name"] for bucket in policy.buckets] + self.closed_statuses
        self.matrix: pd.DataFrame | None = None
        self.transitions = 0               # month-to-month moves the matrix was estimated from

    # ---- fitting --------------------------------------------------------------

    def states_of(self, snapshot_rows: list[dict]) -> pd.DataFrame:
        """The snapshots with their date, balance and state."""
        snaps = pd.DataFrame(snapshot_rows)
        snaps["snapshot_date"] = pd.to_datetime(snaps["snapshot_date"])
        snaps["outstanding_balance"] = pd.to_numeric(snaps["outstanding_balance"])
        dpd = pd.to_numeric(snaps["dpd"]).astype(int)
        closed = snaps["account_status"] == "CLOSED"
        unknown = set(snaps.loc[closed, "status"]) - set(self.closed_statuses)
        if unknown:
            raise ModelError(f"Closed loans with an unknown final status: {sorted(unknown)}")
        snaps["state"] = np.where(closed, snaps["status"], dpd.map(self.policy.bucket_for))
        return snaps.sort_values(["case_uuid", "snapshot_date"]).reset_index(drop=True)

    def fit(self, snapshot_rows: list[dict], until=None) -> "RollRateModel":
        """Estimate the roll rates from month-ends up to `until` (all of them if None), weighted by balance."""
        snaps = self.states_of(snapshot_rows)
        if until is not None:
            snaps = snaps[snaps["snapshot_date"] <= pd.Timestamp(until)]
        snaps["next_state"] = snaps.groupby("case_uuid")["state"].shift(-1)
        moves = snaps[snaps["next_state"].notna() & ~snaps["state"].isin(self.closed_statuses)]
        if moves.empty:
            raise ModelError("No month-to-month moves to learn roll rates from")

        balance = moves.pivot_table(index="state", columns="next_state", values="outstanding_balance",
                                    aggfunc="sum", fill_value=0).reindex(index=self.states, columns=self.states,
                                                                         fill_value=0)
        for state in self.states:
            if balance.loc[state].sum() == 0:      # closed states, and any bucket with no history, stay put
                balance.loc[state, state] = 1
        self.matrix = balance.div(balance.sum(axis=1), axis=0)
        self.transitions = len(moves)
        self.trained = True
        return self

    def predict_pd(self, frame: pd.DataFrame) -> pd.Series:
        """Chance each loan is written off within `horizon` months, from the bucket it is in today."""
        self._check_trained()
        self._check_columns(frame)
        unknown = set(frame["bucket"]) - set(self.states)
        if unknown:
            raise ModelError(f"Unknown buckets: {sorted(unknown)}")
        #WRITTEN_OFF is absorbing, so after `horizon` steps its column holds the chance of reaching it by then
        reached = np.linalg.matrix_power(self.matrix.to_numpy(), self.horizon)
        written_off = pd.Series(reached[:, self.states.index("WRITTEN_OFF")], index=self.states)
        return frame["bucket"].map(written_off).astype(float).rename("pd")

    # ---- projecting -----------------------------------------------------------

    def balances(self, frame: pd.DataFrame, state_column: str = "bucket") -> pd.Series:
        """Total outstanding balance in each state, e.g. from one business date of the portfolio."""
        return frame.groupby(state_column)["outstanding_balance"].sum().reindex(self.states, fill_value=0)

    def project(self, start: pd.Series, months: int = 12) -> pd.DataFrame:
        """Balance in each state at month 0 (start) to `months`; every row adds up to the starting total."""
        self._check_trained()
        if months < 1:
            raise ModelError(f"months must be at least 1, not {months}")
        if set(start.index) - set(self.states):
            raise ModelError(f"Unknown states in the starting balances: {sorted(set(start.index) - set(self.states))}")
        vector = start.reindex(self.states, fill_value=0).astype(float).to_numpy()
        rows = [vector]
        for _ in range(months):
            rows.append(rows[-1] @ self.matrix.to_numpy())
        return pd.DataFrame(rows, columns=self.states).rename_axis("month")

    def expected_write_offs(self, start: pd.Series, horizons: tuple[int, ...] = (3, 6, 12)) -> pd.DataFrame:
        """New write-offs projected by each horizon, in UGX and as a share of the open balance today."""
        projection = self.project(start, max(horizons))
        open_balance = start.reindex(self.states, fill_value=0).drop(self.closed_statuses).sum()
        already = projection.loc[0, "WRITTEN_OFF"]
        return pd.DataFrame([{
            "months ahead": months,
            "written off (UGX)": int(round(projection.loc[months, "WRITTEN_OFF"] - already)),
            "share of open balance %": round(100 * (projection.loc[months, "WRITTEN_OFF"] - already) / open_balance, 1)
            if open_balance else 0.0,
        } for months in horizons])

    # ---- checking against what happened ---------------------------------------

    def actual_path(self, snapshot_rows: list[dict], start, months: int) -> pd.DataFrame:
        """
        Where the balance of the loans open at `start` really went, month by month.

        Measured the same way as a projection: each loan keeps its starting balance and moves with its
        state, so the two can be compared directly to back-test the model.
        """
        snaps = self.states_of(snapshot_rows)
        start = pd.Timestamp(start)
        dates = sorted(snaps["snapshot_date"].unique())
        if start not in dates:
            raise ModelError(f"No snapshots on {start:%Y-%m-%d}")
        position = dates.index(start)
        if position + months >= len(dates):
            raise ModelError(f"Only {len(dates) - position - 1} months of history after {start:%Y-%m-%d}")

        cohort = snaps[(snaps["snapshot_date"] == start) & ~snaps["state"].isin(self.closed_statuses)]
        weights = cohort.set_index("case_uuid")["outstanding_balance"]
        later = snaps[snaps["case_uuid"].isin(weights.index)]
        rows = []
        for step in range(months + 1):
            day = dates[position + step]
            #Note: a loan with no snapshot that month has closed earlier and stays in its closing state
            last = later[later["snapshot_date"] <= day].groupby("case_uuid")["state"].last()
            rows.append(weights.groupby(last.reindex(weights.index)).sum().reindex(self.states, fill_value=0))
        return pd.DataFrame(rows, columns=self.states).reset_index(drop=True).rename_axis("month")
