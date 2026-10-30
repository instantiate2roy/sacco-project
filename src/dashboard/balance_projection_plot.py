from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class BalanceProjectionPlot(DashboardPlot):
    """
    The roll-rate projection of the selected loans' balance by state, month by month.
    """

    title = "Projected balance of today's loans (not yet settled)"
    xlabel = "months ahead"
    ylabel = "UGX million"

    def draw(self, ax: Axes) -> None:
        if len(self.view.projection):
            shown = self.view.projection.drop(columns="SETTLED") / 1e6
            ax.stackplot(shown.index, shown.T.to_numpy(), labels=list(shown.columns))
            ax.legend(loc="upper left", fontsize=7)
        else:
            ax.text(0.5, 0.5, "Shown for the latest business date", ha="center", va="center")
