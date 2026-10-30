import pandas as pd

from .display import Display
from .choice_filter import ChoiceFilter


class BucketComparisonList(Display):
    """
    Each open loan's bucket by days past due (DPD) against its bucket by months in arrears (MIA).

    Rows are the DPD buckets and columns the MIA buckets, both in the policy's order. Loans on
    the diagonal land in the same bucket either way; the rest are where the two measures disagree,
    for example a borrower who pays part of each instalment.
    """

    title = "Buckets by DPD and by MIA"
    sort_by = ["order"]

    def __init__(self, loans: pd.DataFrame, policy, business_date,
                 list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.loans = loans
        self.buckets = [bucket["name"] for bucket in policy.buckets]
        self.columns = ["by DPD", *[f"MIA {name}" for name in self.buckets], "total"]
        same = int((loans["bucket"] == loans["mia_bucket"]).sum())
        self.subtitle = (f"{len(loans):,} open loans on {pd.Timestamp(business_date):%d %B %Y}: "
                         f"{same:,} ({same / len(loans):.1%}) are in the same bucket by both measures, "
                         f"{len(loans) - same:,} are not")
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        counts = pd.crosstab(self.loans["bucket"], self.loans["mia_bucket"])
        # every bucket on both sides, in the policy's order, even if no loan is in it
        counts = counts.reindex(index=self.buckets, columns=self.buckets, fill_value=0)
        counts.columns = [f"MIA {name}" for name in counts.columns]
        counts["total"] = counts.sum(axis=1)

        table = counts.rename_axis("by DPD").reset_index()
        table["order"] = range(len(table))
        return table

    def build_filters(self):
        return [ChoiceFilter("by DPD", "By DPD", width="400px")]