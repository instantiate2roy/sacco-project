from .dashboard_list import DashboardList


class WriteOffProjectionList(DashboardList):
    """
    New write-offs the roll-rate projection expects from the selected loans by each horizon.
    """

    title = "Projected new write-offs"
    columns = ["months ahead", "written off (UGX)", "share of open balance %"]
    sort_by = ["months ahead"]
    sort_ascending = True

    def table(self, view):
        return view.write_offs
