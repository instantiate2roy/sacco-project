from datetime import datetime

import pandas as pd

from src.dunning import DunningEngine

RUN_AT = datetime(2026, 10, 23, 9, 0)


def loans(*rows):
    columns = ["case_uuid", "customer_uuid", "dpd", "profile", "bucket", "current_treatment"]
    return pd.DataFrame([dict(zip(columns, row)) for row in rows], columns=columns)


def contacts(*pairs):
    return [{"customer_uuid": customer, "contact_type_id": kind, "value": "x", "valid": "Y"} for customer, kind in pairs]


def treatments(actions):
    return {a.case_uuid: a.treatment for a in actions}


def test_treatment_comes_from_the_matrix(policy):
    engine = DunningEngine(policy, contacts(("c1", "MOBILE_PHONE")))
    actions = engine.propose(loans(("k1", "c1", 10, "low_risk", "1-30", "")), RUN_AT)

    assert treatments(actions) == {"k1": "SMS"}
    assert actions[0].planned_at == RUN_AT and actions[0].profile == "low_risk"


def test_loans_not_overdue_or_without_a_treatment_get_nothing(policy):
    engine = DunningEngine(policy, contacts(("c1", "MOBILE_PHONE")))
    actions = engine.propose(loans(("k1", "c1", 0, "current", "current", ""),
                                   ("k2", "c1", 95, "low_risk", "90+", "")), RUN_AT)
    assert actions == []


def test_unreachable_channel_falls_back(policy):
    # SMS falls back to EMAIL in the policy; CALL falls back to SMS
    engine = DunningEngine(policy, contacts(("c1", "EMAIL")))
    actions = engine.propose(loans(("k1", "c1", 10, "low_risk", "1-30", "")), RUN_AT)
    assert treatments(actions) == {"k1": "EMAIL"}


def test_no_valid_contact_at_all_means_no_action(policy):
    engine = DunningEngine(policy, [{"customer_uuid": "c1", "contact_type_id": "MOBILE_PHONE", "value": "x",
                                     "valid": "N"}])
    assert engine.propose(loans(("k1", "c1", 10, "low_risk", "1-30", "")), RUN_AT) == []


def test_a_case_already_referred_is_not_referred_again(policy):
    engine = DunningEngine(policy, [])
    actions = engine.propose(loans(("k1", "c1", 120, "high_risk", "90+", "DCA"),
                                   ("k2", "c2", 120, "high_risk", "90+", "")), RUN_AT)
    assert treatments(actions) == {"k2": "DCA"}
