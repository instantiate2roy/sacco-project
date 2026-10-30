from .dashboard_list import DashboardList
from .text_filter import TextFilter


class ExpectedLossList(DashboardList):
    """
    The selected loans, highest expected loss (PD x outstanding balance) first.
    """

    title = "Loans by expected loss"
    columns = ["account_no", "customer", "profile", "tier", "bucket", "mia_bucket", "dpd", "mia",
               "outstanding_balance", "arrears_amount", "pd", "expected_loss", "reachability", "assigned_to"]
    sort_by = ["expected_loss"]
    sort_ascending = False
    decimals = 2

    def __init__(self, view, list_page_size: int = 25, filter_cols_per_row: int = 3):
        super().__init__(view, list_page_size, filter_cols_per_row)

    def table(self, view):
        return view.loans

    def build_filters(self):
        return [TextFilter("customer", "Customer"), TextFilter("account_no", "Account")]
