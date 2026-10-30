import pandas as pd

from .display import Display
from .choice_filter import ChoiceFilter

class BalanceProjectionList(Display):
    """
    Where today's open balance is projected to be after a number of months, by state, in UGX million.

    The projection follows today's loans only: each row adds up to today's total, as balance moves
    between buckets, is settled or is written off. WriteOffForecastList shows the write-offs alone.
    """

    title = "Projected balance by state (UGX million)"
    sort_by = ["months ahead"]
    decimals = 1

    def __init__(self, roll_rates, start: pd.Series, months: tuple[int, ...] = (0, 3, 6, 12),
                 business_date=None, list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.roll_rates = roll_rates
        self.start = start
        self.months = months
        self.columns = ["months ahead", *roll_rates.states, "total"]

        when = f" on {pd.Timestamp(business_date):%d %B %Y}" if business_date is not None else ""
        self.subtitle = f"Starting from UGX {start.sum() / 1e6:,.1f} million open{when}"
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        projection = self.roll_rates.project(self.start, max(self.months)).loc[list(self.months)] / 1e6
        projection["total"] = projection.sum(axis=1)       # stays the same every month: nothing leaves the book
        table = projection.rename_axis("months ahead").reset_index()
        table.columns.name = None
        return table

    def build_filters(self):
        return [ChoiceFilter("months ahead", "Months ahead", width="400px")]