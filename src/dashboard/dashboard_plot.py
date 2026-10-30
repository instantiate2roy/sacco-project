from ..plot import Plot
from .dashboard_view import DashboardView


class DashboardPlot(Plot):
    """
    One dashboard chart, drawn from a dashboard view; a new one is made each time the filters change.
    """

    def __init__(self, view: DashboardView):
        self.view = view
