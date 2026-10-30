from .dashboard_list import DashboardList


class BucketBalanceList(DashboardList):
    """
    Loans and balance in each bucket, bucketed by days past due (DPD) and by months in arrears (MIA).
    """

    title = "Buckets by DPD and MIA"
    columns = ["bucket", "loans_by_dpd", "balance_by_dpd", "loans_by_mia", "balance_by_mia"]
    sort_by = []
    sort_ascending = True

    def table(self, view):
        return view.buckets
