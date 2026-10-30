import pandas as pd

from .display import Display
from .text_filter import TextFilter


class ProfileTierList(Display):
    """
    How many open loans fall in each profile and risk tier on one business date.

    Profiles run down the side in the policy's priority order, risk tiers across the top,
    with a total for each row and a total row at the bottom.
    """

    title = "Profiles by risk tier"
    sort_by = ["order"]

    def __init__(self, loans: pd.DataFrame, policy, business_date,
                 list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.loans = loans
        self.policy = policy
        self.business_date = pd.Timestamp(business_date)
        self.tiers = [tier["name"] for tier in policy.risk_tiers]
        self.columns = ["profile", *self.tiers, "total"]
        overdue = int((loans["dpd"] > 0).sum())
        self.subtitle = (f"{len(loans):,} open loans on {self.business_date:%d %B %Y}, "
                         f"{overdue:,} of them overdue")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        counts = pd.crosstab(self.loans["profile"], self.loans["tier"])
        counts = counts.reindex(columns=self.tiers, fill_value=0)       # every tier, even if empty
        counts["total"] = counts.sum(axis=1)

        # profiles in the order the policy checks them, the default profile after them
        order = [rule["name"] for rule in self.policy.profiles] + [self.policy.default_profile]
        counts = counts.reindex([p for p in order if p in counts.index])
        counts.loc["total"] = counts.sum()

        table = counts.rename_axis("profile").reset_index()
        table.columns.name = None
        table["order"] = range(len(table))                               # keeps 'total' at the bottom
        return table

    def build_filters(self):
        return [TextFilter("profile", "Profile", width="400px")]