from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class WriteOffProjectionPlot(DashboardPlot):
    """
    The new write-offs the roll-rate projection expects by each horizon.
    """

    title = "Projected new write-offs"
    xlabel = "months ahead"
    ylabel = "UGX million"

    def draw(self, ax: Axes) -> None:
        write_offs = self.view.write_offs
        if len(write_offs):
            ax.bar(write_offs["months ahead"].astype(str), write_offs["written off (UGX)"] / 1e6)
