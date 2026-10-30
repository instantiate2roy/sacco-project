import pandas as pd

from .display import Display


class WriteOffForecastList(Display):
    """
    New write-offs a roll-rate model expects from today's open loans by each horizon,
    in UGX and as a share of today's open balance.
    """

    title = "Expected write-offs"
    columns = ["months ahead", "written off (UGX)", "share of open balance %"]
    sort_by = ["months ahead"]
    decimals = 1

    def __init__(self, roll_rates, start: pd.Series, horizons: tuple[int, ...] = (3, 6, 12),
                 business_date=None, list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.roll_rates = roll_rates
        self.start = start
        self.horizons = horizons
        open_balance = start.drop(roll_rates.closed_statuses, errors="ignore").sum()
        when = f" on {pd.Timestamp(business_date):%d %B %Y}" if business_date is not None else ""
        self.subtitle = f"Open balance{when}: UGX {open_balance:,.0f}"
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        return self.roll_rates.expected_write_offs(self.start, self.horizons)

    def build_filters(self):
        return []