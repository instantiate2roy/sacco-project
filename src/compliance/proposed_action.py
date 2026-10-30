from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProposedAction:
    """A treatment the dunning step wants to carry out."""
    case_uuid: str
    customer_uuid: str
    treatment: str              # SMS, EMAIL, CALL, DCA or LEGAL
    planned_at: datetime
    profile: str = ""
    bucket: str = ""
