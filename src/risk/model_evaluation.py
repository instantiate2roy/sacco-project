from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class ModelEvaluation:
    """
    How well a model ranks risk on data it wasn't trained on.
    """
    auc: float                 #0.5 is guessing, 1.0 is perfect ranking
    rows: int
    defaults: int
    default_rate: float
    bands: pd.DataFrame        #default rate in each score band, lowest risk first