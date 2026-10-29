import pandas as pd

from .display import Display
from .filters import TextFilter


class ModelComparisonList(Display):
    """
    Several risk models tested on the same months, side by side.

    Useful for seeing how much a group of features adds: train one model with them and one
    without, then compare how well each ranks risk (AUC) and how well each picks out defaults.
    """

    title = "Model comparison"
    columns = ["model", "features", "left out", "AUC", "default rate in riskiest band"]
    sort_by = ["AUC"]
    sort_ascending = False
    decimals = 3

    def __init__(self, models: dict, test: pd.DataFrame, all_features: list[str], bands: int = 5,
                 list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.models = models                     # e.g. {"All features": model, "No arrears": no_arrears_model}
        self.test = test
        self.all_features = all_features
        self.bands = bands
        self.subtitle = (f"All models tested on the same {len(test):,} rows "
                         f"({int(test['defaulted'].sum())} defaults). "
                         f"AUC: 0.5 = guessing, 1.0 = perfect ranking.")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        rows = []
        for name, model in self.models.items():
            evaluation = model.evaluate(self.test, bands=self.bands)
            left_out = [f for f in self.all_features if f not in model.features]
            riskiest = evaluation.bands.iloc[-1]
            rows.append({
                "model": name,
                "features": len(model.features),
                "left out": ", ".join(left_out) or "-",
                "AUC": round(evaluation.auc, 3),
                "default rate in riskiest band": f"{riskiest['default_rate']:.1%}",
            })
        return pd.DataFrame(rows)

    def build_filters(self):
        return [TextFilter("model", "Model", width="400px")]