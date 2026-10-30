import ipywidgets as widgets
import pandas as pd

from .filter import Filter


class TextFilter(Filter):
    """Keeps rows whose column contains the typed text, ignoring case."""

    def __init__(self, column: str, label: str, max_length: int | None = None, width: str = "100%"):
        super().__init__(column, label, width)
        self.max_length = max_length

    def _make_widget(self, values):
        box = widgets.Text(description=self.label, placeholder="type to search")
        if self.max_length:
            box.observe(self._trim, names="value")
        return box

    def _trim(self, change):
        if len(change["new"]) > self.max_length:
            self.widget.value = change["new"][: self.max_length]

    def mask(self, frame):
        text = self.widget.value.strip()
        if not text:
            return pd.Series(True, index=frame.index)
        return frame[self.column].astype(str).str.contains(text, case=False, regex=False)

    def reset(self):
        self.widget.value = ""
