from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class LoansByBucketPlot(DashboardPlot):
    """
    Loans in each bucket, bucketed by days past due and by months in arrears.
    """

    title = "Loans by bucket"
    ylabel = "loans"

    def draw(self, ax: Axes) -> None:
        buckets = self.view.buckets
        if len(buckets):
            x = range(len(buckets))
            ax.bar([i - 0.2 for i in x], buckets["loans_by_dpd"], width=0.4, label="by DPD")
            ax.bar([i + 0.2 for i in x], buckets["loans_by_mia"], width=0.4, label="by MIA")
            ax.set_xticks(list(x), buckets["bucket"])
            ax.legend()
