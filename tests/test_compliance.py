from datetime import date, datetime

import pandas as pd
import pytest

from src.compliance import (CaseStatusRule, ComplianceChecker, ContactHoursRule, DailyChannelLimitRule,
                            DailyContactCapRule, MinimumGapRule, PromisePendingRule, ProposedAction,
                            WeeklyChannelLimitRule)

# Thursday 22 October 2026, 10:00: inside the policy's contact hours (08:00-18:00, Mon-Sat)
THURSDAY_10AM = datetime(2026, 10, 22, 10, 0)
OPEN_CASE = {"status": "OPEN", "ptp_pending_until": None}


def action(treatment="SMS", when=THURSDAY_10AM, case="k1", customer="c1"):
    return ProposedAction(case, customer, treatment, when)


def history(*contacts):
    """Past contacts as (datetime, channel) pairs."""
    return pd.DataFrame({"contact_datetime": pd.to_datetime([c[0] for c in contacts]),
                         "channel": [c[1] for c in contacts]})


NO_HISTORY = history()


def test_case_status_rule_blocks_closed_and_held_cases(policy):
    rule = CaseStatusRule(policy)
    assert rule.check(action(), NO_HISTORY, OPEN_CASE).allowed
    outcome = rule.check(action(), NO_HISTORY, {"status": "ON_HOLD"})
    assert not outcome.allowed and outcome.reason == "case is ON_HOLD"


def test_promise_pending_rule_holds_until_the_promised_date(policy):
    rule = PromisePendingRule(policy)
    case = {"status": "OPEN", "ptp_pending_until": date(2026, 10, 25)}
    assert not rule.check(action(), NO_HISTORY, case).allowed
    assert rule.check(action(when=datetime(2026, 10, 26, 10)), NO_HISTORY, case).allowed


@pytest.mark.parametrize("when, allowed", [
    (datetime(2026, 10, 22, 7, 59), False),     # before 08:00
    (datetime(2026, 10, 22, 8, 0), True),
    (datetime(2026, 10, 22, 18, 0), False),     # the end time itself is outside
    (datetime(2026, 10, 25, 10, 0), False),     # Sunday
])
def test_contact_hours_rule(policy, when, allowed):
    assert ContactHoursRule(policy).check(action(when=when), NO_HISTORY, OPEN_CASE).allowed is allowed


def test_contact_hours_do_not_apply_to_referrals(policy):
    sunday_night = datetime(2026, 10, 25, 23, 0)
    assert ContactHoursRule(policy).check(action("DCA", sunday_night), NO_HISTORY, OPEN_CASE).allowed


def test_daily_channel_limit_counts_the_same_channel_on_the_same_day(policy):
    rule = DailyChannelLimitRule(policy)     # SMS: 1 a day
    assert rule.check(action(), history(("2026-10-21 10:00", "SMS")), OPEN_CASE).allowed
    assert rule.check(action(), history(("2026-10-22 08:30", "EMAIL")), OPEN_CASE).allowed
    assert not rule.check(action(), history(("2026-10-22 08:30", "SMS")), OPEN_CASE).allowed


def test_weekly_channel_limit_counts_the_last_seven_days(policy):
    rule = WeeklyChannelLimitRule(policy)    # SMS: 3 a week
    three_this_week = history(("2026-10-16 11:00", "SMS"), ("2026-10-18 11:00", "SMS"), ("2026-10-20 11:00", "SMS"))
    assert not rule.check(action(), three_this_week, OPEN_CASE).allowed
    one_too_old = history(("2026-10-15 09:00", "SMS"), ("2026-10-18 11:00", "SMS"), ("2026-10-20 11:00", "SMS"))
    assert rule.check(action(), one_too_old, OPEN_CASE).allowed


def test_minimum_gap_rule(policy):
    rule = MinimumGapRule(policy)            # SMS: 24 hours
    outcome = rule.check(action(), history(("2026-10-21 16:00", "SMS")), OPEN_CASE)
    assert not outcome.allowed and "18.0 hours ago" in outcome.reason
    assert rule.check(action(), history(("2026-10-21 09:00", "SMS")), OPEN_CASE).allowed


def test_daily_contact_cap_counts_every_channel(policy):
    rule = DailyContactCapRule(policy)       # 2 contacts a day
    two_today = history(("2026-10-22 08:10", "EMAIL"), ("2026-10-22 08:20", "CALL"))
    assert not rule.check(action(), two_today, OPEN_CASE).allowed
    assert rule.check(action("LEGAL"), two_today, OPEN_CASE).allowed


def make_checker(policy, contacts=(), cases=None, promises=()):
    cases = cases or [{"uuid": "k1", "customer_uuid": "c1", "status": "OPEN"},
                      {"uuid": "k2", "customer_uuid": "c1", "status": "OPEN"}]
    return ComplianceChecker(policy, list(contacts), cases, list(promises))


def test_checker_stops_at_the_first_blocking_rule(policy):
    checker = make_checker(policy, cases=[{"uuid": "k1", "customer_uuid": "c1", "status": "SETTLED"}])
    decision = checker.check(action(when=datetime(2026, 10, 25, 10)))     # settled AND on a Sunday

    assert not decision.allowed
    assert decision.blocked_by == "Case status"
    assert len(decision.outcomes) == 1


def test_checker_counts_contacts_allowed_earlier_in_the_same_run(policy):
    checker = make_checker(policy)
    first = checker.check(action(case="k1"))
    second = checker.check(action(case="k2", when=datetime(2026, 10, 22, 11)))   # same customer, other loan

    assert first.allowed
    assert not second.allowed and second.blocked_by == "Daily channel limit"


def test_checker_holds_cases_with_a_pending_promise(policy):
    promises = [{"case_uuid": "k1", "promised_date": "2026-10-30", "status": "PENDING"},
                {"case_uuid": "k1", "promised_date": "2026-10-01", "status": "BROKEN"}]
    decision = make_checker(policy, promises=promises).check(action())
    assert decision.blocked_by == "Promise pending"
    assert decision.reason == "promise to pay due 2026-10-30"


def test_checker_reads_contacts_through_the_case(policy):
    contacts = [{"case_uuid": "k2", "contact_datetime": "2026-10-22 08:00:00", "channel": "SMS"}]
    decision = make_checker(policy, contacts=contacts).check(action(case="k1"))
    assert decision.blocked_by == "Daily channel limit"


def test_check_all_returns_one_row_per_action(policy):
    frame = make_checker(policy).check_all([action(case="k1"), action("DCA", case="k2")])

    assert list(frame.columns) == ["case_uuid", "customer_uuid", "profile", "bucket", "treatment", "planned_at",
                                   "allowed", "blocked_by", "reason"]
    assert frame["allowed"].tolist() == [True, True]
