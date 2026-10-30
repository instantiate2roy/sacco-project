from abc import ABC, abstractmethod

import ipywidgets as widgets
import pandas as pd

from .error import DisplayError


class Filter(ABC):
    """
    One filter on a list, e.g. a search box or a dropdown.

    Each filter owns its widget and knows which rows of a table it keeps.
    """

    def __init__(self, column: str, label: str, width: str = "100%"):
        self.column = column
        self.label = label
        self.width = width
        self.widget: widgets.Widget | None = None

    def build(self, frame: pd.DataFrame) -> widgets.Widget:
        """Create the widget, using the table to set things like dropdown options."""
        if self.column not in frame.columns:
            raise DisplayError(f"Filter '{self.label}' refers to unknown column '{self.column}'")
        self.widget = self._make_widget(frame[self.column])
        return self.widget

    @abstractmethod
    def _make_widget(self, values: pd.Series) -> widgets.Widget:
        """Create the widget for this kind of filter."""

    @abstractmethod
    def mask(self, frame: pd.DataFrame) -> pd.Series:
        """True for each row the filter keeps."""

    @abstractmethod
    def reset(self) -> None:
        """Put the widget back to 'show everything'."""
