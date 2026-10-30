from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class ReachabilityPlot(DashboardPlot):
    """
    Loans by the share of contact attempts in the last 90 days that reached the customer.
    """

    title = "Reachability (last 90 days)"
    ylabel = "loans"

    def draw(self, ax: Axes) -> None:
        reach = self.view.reachability
        ax.bar(reach["band"].astype(str), reach["loans"])
        ax.tick_params(axis="x", rotation=20)
