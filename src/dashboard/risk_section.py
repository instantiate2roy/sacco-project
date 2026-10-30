from ..display import ProfileBalanceList, TierBalanceList
from .dashboard_section import DashboardSection
from .profile_balance_plot import ProfileBalancePlot
from .tier_balance_plot import TierBalancePlot


class RiskSection(DashboardSection):
    """
    Balance and expected loss by risk tier, and balance by collection profile.
    """

    title = "Risk tiers and profiles"
    plots = [TierBalancePlot, ProfileBalancePlot]
    lists = [TierBalanceList, ProfileBalanceList]
