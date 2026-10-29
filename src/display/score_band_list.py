import pandas as pd

from .display import Display
from .filters import ChoiceFilter


class ScoreBandList(Display):
    """
    How well a risk model ranks loans on months it wasn't trained on.

    The test loans are split into equal-sized bands by predicted PD, from A (lowest) to the
    riskiest band. A good model's predicted PD should be close to the actual default rate in
    each band, and the default rate should rise from band to band.
    """

    title = "Score bands"
    columns = ["band", "loans", "defaults", "predicted PD %", "actual default rate %"]
    sort_by = ["band"]
    decimals = 1

    def __init__(self, evaluation, list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.evaluation = evaluation
        self.subtitle = (
            f"AUC on the test months: {evaluation.auc:.3f} (0.5 = guessing, 1.0 = perfect ranking)<br>"
            f"{evaluation.rows:,} test rows, {evaluation.defaults:,} defaults ({evaluation.default_rate:.1%})")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        bands = self.evaluation.bands.copy()
        bands["band"] = bands["band"].astype(str)
        bands["predicted PD %"] = 100 * bands["average_pd"]
        bands["actual default rate %"] = 100 * bands["default_rate"]
        return bands

    def build_filters(self):
        return [ChoiceFilter("band", "Band", width="400px")]