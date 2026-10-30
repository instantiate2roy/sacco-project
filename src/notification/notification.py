from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Notification:
    created_at: datetime
    case_uuid: str
    account_no: str
    customer: str
    channel: str            #examples SMS, EMAIL, CALL, DCA or LEGAL
    recipient: str          #like phone number, email address, or who the case is referred to
    message: str
    status: str             #sample statuses SENT, QUEUED, REFERRED or BLOCKED
    reason: str = ""        #why compliance blocked it
