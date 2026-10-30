import pandas as pd

from .display import Display
from .choice_filter import ChoiceFilter


class RollRateMatrixList(Display):
    """
    A fitted roll-rate model's matrix: for each state a loan is in at one month-end, the share
    of its balance found in each state a month later.

    Each row adds up to 100%. The diagonal is the balance that stays where it is; to the right
    of it, balance rolling to worse buckets; to the left, balance curing. SETTLED and
    WRITTEN_OFF keep 100% because a closed loan stays closed.
    """

    title = "Roll rates (% of balance, one month later)"
    sort_by = ["order"]
    decimals = 1

    def __init__(self, roll_rates, list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.roll_rates = roll_rates
        self.columns = ["from", *roll_rates.states]
        self.subtitle = (f"Learnt from {roll_rates.transitions:,} month-to-month moves. "
                         f"Read across a row: where that state's balance was a month later.")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        table = (100 * self.roll_rates.matrix).rename_axis("from").reset_index()
        table.columns.name = None
        table["order"] = range(len(table))           # states in the model's order, not alphabetical
        return table

    def build_filters(self):
        return [ChoiceFilter("from", "From", width="400px")]