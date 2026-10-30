import pandas as pd
from matplotlib.axes import Axes
from sklearn.metrics import roc_curve

from .plot import Plot


class RocCurvePlot(Plot):
    """
    How well the model separates defaults from good loans: the further the curve bows
    towards the top left, the better. The dashed line is what guessing would give.
    """

    title = "ROC curve"
    xlabel = "Share of good loans flagged"
    ylabel = "Share of defaults caught"

    def __init__(self, model, test: pd.DataFrame, auc: float, label: str = "defaulted"):
        self.model = model
        self.test = test
        self.auc = auc
        self.label = label

    def draw(self, ax: Axes) -> None:
        flagged, caught, _ = roc_curve(self.test[self.label], self.model.predict_pd(self.test))
        ax.plot(flagged, caught, label=f"{self.model.name} (AUC {self.auc:.2f})")
        ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="Guessing")
        ax.legend()
