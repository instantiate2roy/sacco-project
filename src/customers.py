from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class CustomerNames:
    """
    Customers' names as the lists show them: surname, then given name.

    Built once from the customer rows, then used to add a 'customer' column to any table
    that has a customer_uuid. A customer missing from customer.csv is shown as `missing`,
    so the row stays visible and easy to spot.
    """

    customer_rows: list[dict] = field(repr=False)
    missing: str = "(customer not found)"

    @property
    def table(self) -> pd.DataFrame:
        """Each customer's uuid (as customer_uuid) and name."""
        customers = pd.DataFrame(self.customer_rows, columns=["uuid", "surname", "given_name"])
        return pd.DataFrame({"customer_uuid": customers["uuid"],
                             "customer": customers["surname"] + " " + customers["given_name"]})

    def add_to(self, frame: pd.DataFrame) -> pd.DataFrame:
        """`frame` with a 'customer' column joined on its customer_uuid; no row is dropped."""
        named = frame.merge(self.table, how="left", on="customer_uuid")
        named["customer"] = named["customer"].fillna(self.missing)
        return named