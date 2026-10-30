import pandas as pd

from .display import Display
from .choice_filter import ChoiceFilter


class BacktestList(Display):
    """
    A back-test of a roll-rate model: what it projected for the loans open on a past date,
    against what actually happened to them.

    Both are shown as a share of the balance open on that date, for a few states and horizons,
    so a projected figure and its actual figure sit side by side.
    """

    title = "Back-test: projected against actual (% of the starting balance)"
    sort_by = ["months ahead"]
    decimals = 1

    def __init__(self, projected: pd.DataFrame, actual: pd.DataFrame, start: pd.Series, backtest_from,
                 months: tuple[int, ...] = (3, 6, 12), states: tuple[str, ...] = ("90+", "SETTLED", "WRITTEN_OFF"),
                 list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.projected = projected
        self.actual = actual
        self.start = start
        self.months = list(months)
        self.states = list(states)
        # a display table has one header row, so each state gets a 'projected' and an 'actual' column
        self.columns = ["months ahead", *[f"{state} {kind}" for state in self.states
                                          for kind in ("projected %", "actual %")]]
        self.subtitle = (f"Model fitted on month-ends up to {pd.Timestamp(backtest_from):%d %B %Y}, then run on the "
                         f"UGX {start.sum() / 1e6:,.1f} million open that day and compared with what happened")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        total = self.start.sum()
        table = pd.DataFrame({"months ahead": self.months})
        for state in self.states:
            for kind, frame in (("projected %", self.projected), ("actual %", self.actual)):
                table[f"{state} {kind}"] = (100 * frame.loc[self.months, state] / total).to_numpy()
        return table

    def build_filters(self):
        return [ChoiceFilter("months ahead", "Months ahead", width="400px")]