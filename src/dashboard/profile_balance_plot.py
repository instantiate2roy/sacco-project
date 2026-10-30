from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class ProfileBalancePlot(DashboardPlot):
    """
    Balance in each collection profile.
    """

    title = "Balance by profile"
    xlabel = "UGX million"

    def draw(self, ax: Axes) -> None:
        profiles = self.view.profiles
        if len(profiles):
            ax.barh(profiles["profile"], profiles["balance"] / 1e6)
