from .dashboard_list import DashboardList


class TierBalanceList(DashboardList):
    """
    Loans, balance, average PD % and expected loss in each risk tier.
    """

    title = "Risk tiers"
    columns = ["tier", "loans", "balance", "average_pd", "expected_loss"]
    sort_by = ["tier"]
    sort_ascending = True

    def table(self, view):
        return view.tiers
