from ..display import ExpectedLossList
from .dashboard_section import DashboardSection


class TopLoansSection(DashboardSection):
    """
    The selected loans, highest expected loss (PD x outstanding balance) first.
    """

    title = "Loans with the highest expected loss"
    lists = [ExpectedLossList]
