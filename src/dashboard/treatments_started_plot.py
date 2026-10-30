from matplotlib.axes import Axes

from .dashboard_plot import DashboardPlot


class TreatmentsStartedPlot(DashboardPlot):
    """
    Treatments started in the period, by treatment type.
    """

    title = "Treatments started in the period"
    ylabel = "treatments"

    def draw(self, ax: Axes) -> None:
        treatments = self.view.treatments
        if len(treatments):
            ax.bar(treatments["treatment_type_id"], treatments["started"])
