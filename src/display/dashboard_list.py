from abc import abstractmethod

import pandas as pd

from .display import Display


class DashboardList(Display):
    """
    A dashboard table as a list: it shows one table of a dashboard view and follows the dashboard filters.

    Subclasses set title and columns and say which table of the view they show, in table().
    update() swaps in the view for new filters. Any filters of a list's own must be TextFilters:
    their widget doesn't depend on the rows, so it stays right when the rows change.
    """

    decimals = 1
    thousands = ","

    def __init__(self, view, list_page_size: int = 10, filter_cols_per_row: int = 3):
        self.view = view
        super().__init__(list_page_size, filter_cols_per_row)

    @abstractmethod
    def table(self, view) -> pd.DataFrame:
        """
        The table of the view this list shows.
        """

    def build_frame(self) -> pd.DataFrame:
        return self.table(self.view)

    def build_filters(self):
        return []

    def update(self, view) -> None:
        """
        Show the table of a new view, from the first page.
        """
        self.view = view
        self.frame = self.build_frame()
        self._check_columns()
        self.page = 1
        self._refresh()
