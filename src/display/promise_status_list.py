from .dashboard_list import DashboardList


class PromiseStatusList(DashboardList):
    """
    Promises to pay that fell due in the period, by how they ended.
    """

    title = "Promises due in the period"
    columns = ["status", "promises", "promised", "paid"]
    sort_by = ["promises"]
    sort_ascending = False

    def table(self, view):
        return view.promises
