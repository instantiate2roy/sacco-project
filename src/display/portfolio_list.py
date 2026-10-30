import pandas as pd

from .display import Display
from .choice_filter import ChoiceFilter
from .range_filter import RangeFilter
from .text_filter import TextFilter


class PortfolioList(Display):
    """
    Every open loan on one business date, with its bucket, PD, risk tier and profile,
    highest PD first.
    """

    title = "Profiled loans"
    columns = ["account_no", "customer", "profile", "tier", "pd", "bucket", "mia_bucket", "dpd",
               "outstanding_balance", "reachability", "assigned_to"]
    sort_by = ["pd", "account_no"]
    sort_ascending = [False, True]
    decimals = 3

    def __init__(self, loans: pd.DataFrame, business_date, list_page_size: int = 50,
                 filter_cols_per_row: int = 3):
        self.loans = loans
        self.business_date = pd.Timestamp(business_date)
        overdue = int((loans["dpd"] > 0).sum())
        self.subtitle = (f"{len(loans):,} open loans on {self.business_date:%d %B %Y}, "
                         f"{overdue:,} of them overdue")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        frame = self.loans.copy()
        frame["outstanding_balance"] = frame["outstanding_balance"].astype(int)
        frame["dpd"] = frame["dpd"].astype(int)
        frame["reachability"] = frame["reachability"].astype(float)
        return frame

    def build_filters(self):
        return [
            TextFilter("account_no", "Account no", width="400px"),
            TextFilter("customer", "Customer", width="400px"),
            ChoiceFilter("profile", "Profile", width="400px"),
            ChoiceFilter("tier", "Risk tier", width="400px"),
            ChoiceFilter("bucket", "Bucket", width="400px"),
            ChoiceFilter("assigned_to", "Assigned to", width="400px"),
            RangeFilter("dpd", "DPD", width="400px"),
        ]