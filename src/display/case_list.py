import pandas as pd

from ..customers import Customer
from .display import Display
from .choice_filter import ChoiceFilter
from .range_filter import RangeFilter
from .text_filter import TextFilter


class CaseList(Display):
    """Searchable list of loan cases, showing the customer's name and the loan type."""

    title = "Cases"
    columns = ["account_no", "customer", "loan_type", "status", "dpd", "mia",
               "outstanding_balance", "arrears_amount", "next_due_date"]
    sort_by = ["dpd", "outstanding_balance", "account_no"]
    sort_ascending = [False, False, True]
    missing_customer = Customer.missing  
    missing_loan_type = "(loan type not found)"

    def __init__(self, case_rows: list[dict], customer_rows: list[dict], loan_type_rows: list[dict],
                 list_page_size: int = 50, filter_cols_per_row: int = 3):
        self.case_rows = case_rows
        self.customer_rows = customer_rows
        self.loan_type_rows = loan_type_rows
        super().__init__(list_page_size, filter_cols_per_row)

    def build_frame(self) -> pd.DataFrame:
        cases = pd.DataFrame(self.case_rows)
        for column in ["dpd", "outstanding_balance", "arrears_amount"]:
            cases[column] = pd.to_numeric(cases[column]).astype(int)
        cases["mia"] = pd.to_numeric(cases["mia"])

        cases = Customer(self.customer_rows, missing=self.missing_customer).add_to(cases)

        loan_types = pd.DataFrame(self.loan_type_rows)[["uuid", "name"]].rename(columns={"name": "loan_type"})
        cases = cases.merge(loan_types, how="left", left_on="loan_type_uuid", right_on="uuid",
                            suffixes=("", "_loan_type"))
        # keep cases whose loan type is missing, and make them easy to spot
        return cases.fillna({"loan_type": self.missing_loan_type})

    def build_filters(self):
        return [
            TextFilter("account_no", "Account no", width="400px"),
            TextFilter("customer", "Customer", width="400px"),
            ChoiceFilter("loan_type", "Loan type", width="400px"),
            ChoiceFilter("status", "Status", width="400px"),
            RangeFilter("dpd", "DPD", width="400px"),
            RangeFilter("outstanding_balance", "Outstanding", step=10_000, width="400px"),
        ]