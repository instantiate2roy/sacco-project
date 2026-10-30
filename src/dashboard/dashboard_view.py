from dataclasses import dataclass, field

import pandas as pd


@dataclass
class DashboardView:
    """Everything the dashboard shows for one choice of filters."""
    business_date: pd.Timestamp
    period_start: pd.Timestamp | None
    filters: dict
    summary: dict
    par_trend: pd.DataFrame
    profiles: pd.DataFrame
    buckets: pd.DataFrame
    treatments: pd.DataFrame
    outcomes: pd.DataFrame
    reachability: pd.DataFrame
    compliance: pd.DataFrame
    payments: pd.DataFrame
    promises: pd.DataFrame
    loans: pd.DataFrame
    tiers: pd.DataFrame
    projection: pd.DataFrame          # balance by state, month 0 to 12; empty when not projected
    write_offs: pd.DataFrame          # projected new write-offs at 3, 6 and 12 months
    notes: dict[str, str] = field(default_factory=dict)   # a note for a section, by section (compliance, projection)

    def tables(self) -> dict[str, pd.DataFrame]:
        """The view's tables by name, for exporting."""
        return {"summary": pd.DataFrame([self.summary]), "par_trend": self.par_trend, "profiles": self.profiles,
                "buckets": self.buckets, "treatments": self.treatments, "outcomes": self.outcomes,
                "reachability": self.reachability, "compliance_blocks": self.compliance,
                "payments": self.payments, "promises": self.promises, "loans": self.loans, "tiers": self.tiers,
                "projection": self.projection.reset_index(), "projected_write_offs": self.write_offs}
