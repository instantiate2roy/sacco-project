import pandas as pd

from .display import Display
from .filters import ChoiceFilter, TextFilter


class CoefficientList(Display):
    """
    What a trained logistic PD model learned: each feature's coefficient, strongest first.

    A positive coefficient raises the predicted risk and a negative one lowers it. Numbers were
    scaled before training, so their sizes can be compared. The subtitle says which months the
    model was trained and tested on.
    """

    title = "Model coefficients"
    columns = ["feature", "kind", "coefficient", "effect"]
    sort_by = ["strength"]
    sort_ascending = False
    decimals = 3

    def __init__(self, model, train: pd.DataFrame, test: pd.DataFrame, label: str = "defaulted",
                 list_page_size: int = 12, filter_cols_per_row: int = 3):
        self.model = model
        self.subtitle = (
            f"Training: {len(train):,} rows ({int(train[label].sum())} defaults), "
            f"months up to {train['observed_on'].max():%b %Y}<br>"
            f"Testing: {len(test):,} rows ({int(test[label].sum())} defaults), "
            f"{test['observed_on'].min():%b %Y} to {test['observed_on'].max():%b %Y}")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        table = self.model.coefficients()
        # a category becomes one column per value, e.g. product_salary; numbers keep their name
        table["kind"] = table["feature"].map(lambda f: "number" if f in self.model.numeric else "category")
        table["strength"] = table["coefficient"].abs()
        table["coefficient"] = table["coefficient"].round(3)
        return table

    def build_filters(self):
        return [
            TextFilter("feature", "Feature", width="400px"),
            ChoiceFilter("kind", "Kind", width="400px"),
            ChoiceFilter("effect", "Effect", width="400px"),
        ]