import pytest

from src.exceptions import PolicyError
from src.policy import Policy


@pytest.mark.parametrize("dpd, bucket", [(0, "current"), (1, "1-30"), (30, "1-30"), (31, "31-60"),
                                         (90, "61-90"), (91, "90+"), (5000, "90+")])
def test_bucket_for_uses_the_bucket_edges(policy, dpd, bucket):
    assert policy.bucket_for(dpd) == bucket


@pytest.mark.parametrize("pd_value, tier", [(0.0, "A"), (0.0099, "A"), (0.01, "B"), (0.09, "C"),
                                            (0.49, "D"), (0.5, "E"), (1.0, "E")])
def test_tier_for_takes_the_first_tier_whose_max_pd_is_above(policy, pd_value, tier):
    assert policy.tier_for(pd_value) == tier


@pytest.mark.parametrize("call", [lambda p: p.bucket_for(-1), lambda p: p.tier_for(-0.1), lambda p: p.tier_for(1.1)])
def test_out_of_range_values_are_rejected(policy, call):
    with pytest.raises(PolicyError):
        call(policy)


def test_profile_for_takes_the_first_rule_by_priority(policy):
    facts = {"bucket": "90+", "reachability": 0.2}
    assert policy.profile_for(facts) == "high_risk_unreachable"
    assert policy.profile_for({**facts, "reachability": 0.8}) == "high_risk"


def test_profile_for_missing_fact_does_not_match(policy):
    # no reachability (no contact attempts) must not count as "rarely answers"
    assert policy.profile_for({"bucket": "90+", "reachability": None}) == "high_risk"


def test_profile_for_falls_back_to_the_default_profile(policy):
    assert policy.profile_for({"bucket": "current"}) == "current"


def test_treatment_for_reads_the_matrix(policy):
    assert policy.treatment_for("high_risk", "90+") == "DCA"
    assert policy.treatment_for("low_risk", "90+") is None


def test_load_reports_a_missing_file(tmp_path):
    with pytest.raises(PolicyError, match="not found"):
        Policy.load(tmp_path / "policy.json")


def test_load_reports_invalid_json(tmp_path):
    path = tmp_path / "policy.json"
    path.write_text("{ not json")
    with pytest.raises(PolicyError, match="not valid JSON"):
        Policy.load(path)


def test_unknown_treatment_codes_are_rejected_when_types_are_given(policy_data):
    with pytest.raises(PolicyError, match="unknown treatment"):
        Policy(policy_data, treatment_types=["SMS", "EMAIL"])


def _gap_in_buckets(data):
    data["buckets"]["edges"][1]["upper"] = 29


def _open_bucket_in_the_middle(data):
    data["buckets"]["edges"][2]["upper"] = None


def _tiers_out_of_order(data):
    data["risk_tiers"][1]["max_pd"] = 0.005


def _unknown_profile_field(data):
    data["profiles"][0]["conditions"]["shoe_size"] = {"min": 1}


def _duplicate_priority(data):
    data["profiles"][1]["priority"] = data["profiles"][0]["priority"]


def _matrix_with_unknown_bucket(data):
    data["treatment_matrix"]["low_risk"]["999+"] = "SMS"


def _daily_limit_above_weekly(data):
    data["compliance"]["channels"]["SMS"]["max_per_day"] = 10


def _contact_hours_backwards(data):
    data["compliance"]["contact_hours"]["start"] = "19:00"


def _missing_section(data):
    del data["compliance"]


@pytest.mark.parametrize("change", [_gap_in_buckets, _open_bucket_in_the_middle, _tiers_out_of_order,
                                    _unknown_profile_field, _duplicate_priority, _matrix_with_unknown_bucket,
                                    _daily_limit_above_weekly, _contact_hours_backwards, _missing_section])
def test_inconsistent_policies_are_rejected(make_policy, change):
    with pytest.raises(PolicyError):
        make_policy(change)
