from .sms_template import SmsTemplate
from .email_template import EmailTemplate
from .referral_template import ReferralTemplate
from .call_template import CallTemplate
from .message_template import MessageTemplate
from .notification import Notification
import pandas as pd
from ..compliance import ComplianceDecision
from .error import NotificationError
from dataclasses import asdict, fields

class Log:
    """
    The in-system log of every message the collections run sent, queued, referred or held back.

    loans: the portfolio rows for the run's business date (Profiler.portfolio() for one date).
    The first valid mobile number and email address on record are used, as in the dunning engine.
    """

    templates = [SmsTemplate(), EmailTemplate(), CallTemplate(),
                 ReferralTemplate("DCA", "Debt collection agency"), ReferralTemplate("LEGAL", "Legal department")]

    def __init__(self, loans: pd.DataFrame, customer_rows: list[dict], contact_rows: list[dict],
                 templates: list[MessageTemplate] | None = None):
        self.templates = {template.channel: template for template in (templates or self.templates)}

        contacts = pd.DataFrame(contact_rows, columns=["customer_uuid", "contact_type_id", "value", "valid"])
        valid = contacts[contacts["valid"] == "Y"]
        first = lambda kind: valid[valid["contact_type_id"] == kind].groupby("customer_uuid")["value"].first()
        given_names = {row["uuid"]: row["given_name"] for row in customer_rows}

        details = loans[["case_uuid", "customer_uuid", "account_no", "customer", "dpd", "arrears_amount",
                         "outstanding_balance"]].copy()
        for column in ["dpd", "arrears_amount", "outstanding_balance"]:
            details[column] = details[column].astype(int)
        details["given_name"] = details["customer_uuid"].map(given_names).fillna(details["customer"])
        details["mobile"] = details["customer_uuid"].map(first("MOBILE_PHONE")).fillna("")
        details["email"] = details["customer_uuid"].map(first("EMAIL")).fillna("")
        self._loans = details.set_index("case_uuid").to_dict("index")
        self.entries: list[Notification] = []

    def record(self, decision: ComplianceDecision) -> Notification:
        """
        Write one compliance decision to the log as a notification.
        """
        action = decision.action
        template = self.templates.get(action.treatment)
        if template is None:
            raise NotificationError(f"No message template for the {action.treatment} channel")
        loan = self._loans.get(action.case_uuid)
        if loan is None:
            raise NotificationError(f"Case {action.case_uuid} isn't in the portfolio for this run")
        entry = Notification(
            created_at=action.planned_at, case_uuid=action.case_uuid, account_no=loan["account_no"],
            customer=loan["customer"], channel=template.channel, recipient=template.recipient(loan),
            message=template.render(loan), status=template.status if decision.allowed else "BLOCKED",
            reason="" if decision.allowed else f"{decision.blocked_by}: {decision.reason}")
        self.entries.append(entry)
        return entry

    def record_all(self, decisions: list[ComplianceDecision]) -> list[Notification]:
        return [self.record(decision) for decision in decisions]

    def to_frame(self) -> pd.DataFrame:
        """
        The log as a table, one row per notification.
        """
        return pd.DataFrame([asdict(entry) for entry in self.entries],
                            columns=[f.name for f in fields(Notification)])