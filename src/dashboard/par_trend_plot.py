from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class ParTrendPlot(DashboardPlot):
    """
    PAR30 and PAR90 at every business date, with the selected date marked.
    """

    title = "Portfolio at risk (% of balance)"
    ylabel = "%"

    def draw(self, ax: Axes) -> None:
        trend = self.view.par_trend
        ax.plot(trend["business_date"], trend["PAR30 %"], marker="o", label="PAR30")
        ax.plot(trend["business_date"], trend["PAR90 %"], marker="o", label="PAR90")
        ax.axvline(self.view.business_date, color="grey", linestyle=":", linewidth=1)
        ax.legend()
        ax.tick_params(axis="x", rotation=45)
