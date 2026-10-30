from datetime import datetime

import pandas as pd
import pytest

from src.compliance import ComplianceDecision, ProposedAction, RuleOutcome
from src.notification import (CallTemplate, EmailTemplate, Log, Notification, NotificationError, ReferralTemplate,
                              SmsTemplate)

WHEN = datetime(2026, 10, 23, 9, 0)
LOAN = {"case_uuid": "k1", "customer_uuid": "c1", "account_no": "LN-001", "customer": "Achieng Mary",
        "dpd": 12, "arrears_amount": 150000.0, "outstanding_balance": 1200000.0}


@pytest.fixture
def log():
    contacts = [{"customer_uuid": "c1", "contact_type_id": "MOBILE_PHONE", "value": "0772000001", "valid": "N"},
                {"customer_uuid": "c1", "contact_type_id": "MOBILE_PHONE", "value": "0772000002", "valid": "Y"},
                {"customer_uuid": "c1", "contact_type_id": "EMAIL", "value": "mary@example.com", "valid": "Y"}]
    return Log(pd.DataFrame([LOAN]), [{"uuid": "c1", "given_name": "Mary"}], contacts)


def decision(treatment, allowed=True, case="k1"):
    outcomes = [RuleOutcome("Case status", True)] + ([] if allowed else [RuleOutcome("Contact hours", False, "too late")])
    return ComplianceDecision(ProposedAction(case, "c1", treatment, WHEN), allowed, outcomes)


def test_sms_is_sent_to_the_first_valid_mobile(log):
    entry = log.record(decision("SMS"))

    assert isinstance(entry, Notification)
    assert (entry.channel, entry.status, entry.recipient) == ("SMS", "SENT", "0772000002")
    assert entry.message.startswith("Dear Mary, your loan LN-001 is 12 days overdue")
    assert "UGX 150,000" in entry.message


@pytest.mark.parametrize("treatment, status, recipient", [
    ("EMAIL", "SENT", "mary@example.com"),
    ("CALL", "QUEUED", "0772000002"),
    ("DCA", "REFERRED", "Debt collection agency"),
    ("LEGAL", "REFERRED", "Legal department"),
])
def test_each_channel_gets_its_status_and_recipient(log, treatment, status, recipient):
    entry = log.record(decision(treatment))
    assert (entry.status, entry.recipient) == (status, recipient)


def test_blocked_decisions_are_logged_with_the_rule_and_reason(log):
    entry = log.record(decision("SMS", allowed=False))
    assert entry.status == "BLOCKED"
    assert entry.reason == "Contact hours: too late"


def test_unknown_channel_or_case_is_an_error(log):
    with pytest.raises(NotificationError, match="No message template"):
        log.record(decision("FAX"))
    with pytest.raises(NotificationError, match="isn't in the portfolio"):
        log.record(decision("SMS", case="k9"))


def test_to_frame_has_one_row_per_entry(log):
    log.record_all([decision("SMS"), decision("CALL", allowed=False)])
    frame = log.to_frame()

    assert len(frame) == 2
    assert frame["status"].tolist() == ["SENT", "BLOCKED"]
    assert list(frame.columns)[:3] == ["created_at", "case_uuid", "account_no"]


def test_empty_log_still_has_columns(log):
    assert "status" in log.to_frame().columns


def test_templates_word_their_messages_from_the_loan():
    loan = {**LOAN, "given_name": "Mary", "mobile": "0772", "email": "m@x"}
    assert "Subject: Loan LN-001 is overdue" in EmailTemplate().render(loan)
    assert CallTemplate().render(loan).startswith("Call Achieng Mary about loan LN-001")
    assert "Refer loan LN-001 (Achieng Mary) to Legal" in ReferralTemplate("LEGAL", "Legal").render(loan)
    assert SmsTemplate().recipient(loan) == "0772"
