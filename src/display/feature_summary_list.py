import pandas as pd

from .display import Display
from .filters import TextFilter


class FeatureSummaryList(Display):
    """
    A summary of the risk model's training rows: how many there are, how many defaulted,
    and the mean, lowest and highest value of each numeric feature.
    """

    title = "Training data summary"
    columns = ["feature", "mean", "min", "max"]
    sort_by = ["order"]

    def __init__(self, training_rows: pd.DataFrame, features: list[str], label: str = "defaulted",
                 list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.training_rows = training_rows
        self.features = features
        defaults = int(training_rows[label].sum())
        # the line shown under the title, e.g. "8,906 loan-months, 713 went on to default (8.0%)"
        self.subtitle = (f"{len(training_rows):,} loan-months, {defaults:,} went on to default "
                      f"({defaults / len(training_rows):.1%})")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        summary = self.training_rows[self.features].describe().T[["mean", "min", "max"]].round(2)
        summary = summary.rename_axis("feature").reset_index()
        summary["order"] = range(len(summary))         # keep the features in the order given
        return summary

    def build_filters(self):
        return [TextFilter("feature", "Feature", width="400px")]