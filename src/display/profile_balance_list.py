from .dashboard_list import DashboardList


class ProfileBalanceList(DashboardList):
    """
    Loans, balance and average PD % in each collection profile, largest balance first.
    """

    title = "Profiles"
    columns = ["profile", "loans", "balance", "average_pd"]
    sort_by = ["balance"]
    sort_ascending = False

    def table(self, view):
        return view.profiles
