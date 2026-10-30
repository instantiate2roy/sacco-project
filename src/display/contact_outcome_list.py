from .dashboard_list import DashboardList


class ContactOutcomeList(DashboardList):
    """
    Contacts made in the period by channel and outcome.
    """

    title = "Contact outcomes in the period"
    columns = ["channel", "outcome", "contacts"]
    sort_by = ["channel", "contacts"]
    sort_ascending = [True, False]

    def table(self, view):
        return view.outcomes
