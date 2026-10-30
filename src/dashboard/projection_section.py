from ..display import WriteOffProjectionList
from .balance_projection_plot import BalanceProjectionPlot
from .dashboard_section import DashboardSection
from .write_off_projection_plot import WriteOffProjectionPlot


class ProjectionSection(DashboardSection):
    """
    The roll-rate projection of the selected loans' balance, and the write-offs it expects.
    """

    title = "Projection"
    note = "projection"
    plots = [BalanceProjectionPlot, WriteOffProjectionPlot]
    lists = [WriteOffProjectionList]
