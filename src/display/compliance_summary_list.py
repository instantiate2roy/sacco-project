from datetime import datetime

import pandas as pd

from .display import Display
from .choice_filter import ChoiceFilter


class ComplianceSummaryList(Display):
    """
    The result of one start-of-day compliance check: for each treatment, how many proposed
    actions were allowed and how many each compliance rule blocked.

    Pass rule_names (e.g. [rule.name for rule in checker.rules]) to show every rule, including
    those that blocked nothing; otherwise only the rules that blocked something get a column.
    """

    title = "Compliance check"
    sort_by = ["order"]

    def __init__(self, decisions: pd.DataFrame, run_at: datetime, rule_names: list[str] | None = None,
                 list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.decisions = decisions
        blocked = decisions.loc[~decisions["allowed"], "blocked_by"]
        self.rule_names = rule_names or sorted(blocked.unique())
        self.columns = ["treatment", "allowed", *self.rule_names, "total"]
        self.subtitle = (f"Run at {run_at:%A %d %B %Y %H:%M}: {len(decisions)} actions proposed, "
                         f"{int(decisions['allowed'].sum())} allowed, {len(blocked)} blocked")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        outcome = self.decisions["blocked_by"].where(~self.decisions["allowed"], "allowed")
        counts = pd.crosstab(self.decisions["treatment"], outcome)
        counts = counts.reindex(columns=["allowed", *self.rule_names], fill_value=0)
        counts["total"] = counts.sum(axis=1)
        counts.loc["total"] = counts.sum()

        table = counts.rename_axis("treatment").reset_index()
        table.columns.name = None
        #keeps the total row at the bottom
        table["order"] = range(len(table)) 
        return table

    def build_filters(self):
        return [ChoiceFilter("treatment", "Treatment", width="400px")]