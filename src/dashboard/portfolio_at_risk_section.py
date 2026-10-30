from ..display import BucketBalanceList
from .dashboard_section import DashboardSection
from .loans_by_bucket_plot import LoansByBucketPlot
from .par_trend_plot import ParTrendPlot


class PortfolioAtRiskSection(DashboardSection):
    """
    PAR30 and PAR90 over time, and the loans in each bucket by days past due and by months in arrears.
    """

    title = "Portfolio at risk"
    plots = [ParTrendPlot, LoansByBucketPlot]
    lists = [BucketBalanceList]
