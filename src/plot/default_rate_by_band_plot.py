from matplotlib.axes import Axes

from .plot import Plot


class DefaultRateByBandPlot(Plot):
    """
    The actual default rate in each score band; it should rise from A to the riskiest band.
    """

    title = "Default rate by score band"
    xlabel = "Score band (A = lowest predicted risk)"
    ylabel = "Actual default rate %"

    def __init__(self, evaluation):
        self.evaluation = evaluation

    def draw(self, ax: Axes) -> None:
        bands = self.evaluation.bands
        ax.bar(bands["band"].astype(str), 100 * bands["default_rate"])