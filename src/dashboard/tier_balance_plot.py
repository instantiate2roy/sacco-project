from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class TierBalancePlot(DashboardPlot):
    """
    Balance and expected loss in each risk tier.
    """

    title = "Balance by risk tier (A = lowest PD)"
    ylabel = "UGX million"

    def draw(self, ax: Axes) -> None:
        tiers = self.view.tiers
        if len(tiers):
            ax.bar(tiers["tier"], tiers["balance"] / 1e6, label="balance")
            ax.bar(tiers["tier"], tiers["expected_loss"] / 1e6, label="expected loss")
            ax.legend()
