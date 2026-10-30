from .dashboard_list import DashboardList


class ComplianceBlockList(DashboardList):
    """
    How many treatments proposed for the latest start-of-day run each compliance rule blocked.
    """

    title = "Treatments blocked by each compliance rule"
    columns = ["rule", "blocked"]
    sort_by = ["blocked"]
    sort_ascending = False

    def table(self, view):
        return view.compliance
