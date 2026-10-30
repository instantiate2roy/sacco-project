from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot
from .dashboard_view import DashboardView


class PromisesDuePlot(DashboardPlot):
    """
    Promises to pay that fell due in the period, by how they ended.
    """

    ylabel = "promises"

    def __init__(self, view: DashboardView):
        super().__init__(view)
        self.title = f"Promises due in the period (keep rate {view.summary['promise keep rate %']}%)"

    def draw(self, ax: Axes) -> None:
        promises = self.view.promises
        if len(promises):
            ax.bar(promises["status"], promises["promises"])
