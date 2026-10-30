"""
Shared fixtures: the real policy file, and one run of the whole pipeline on the synthetic data in data/.

The pipeline fixture is built once per test session (a few seconds) and shared by the integration tests.
"""
import copy
import json
from datetime import datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")      # draw charts off screen; must come before pyplot is imported

import pytest

from src.compliance import ComplianceChecker
from src.csv_import import CsvImport
from src.dashboard import DashboardData
from src.dunning import DunningEngine
from src.notification import Log
from src.policy import Policy
from src.profiler import Profiler
from src.risk import FeatureBuilder, LogisticPdModel, RollRateModel
from src.synthetic_core_banking import GeneratorSettings

ROOT = Path(__file__).resolve().parent.parent
POLICY_FILE = ROOT / "data" / "configs" / "policy.json"


@pytest.fixture(scope="session")
def policy_data() -> dict:
    return json.loads(POLICY_FILE.read_text())


@pytest.fixture(scope="session")
def policy(policy_data) -> Policy:
    return Policy(copy.deepcopy(policy_data))


@pytest.fixture
def make_policy(policy_data):
    """
    Build a Policy from a copy of the real one, after `change(data)` has edited it.
    """
    def build(change=None):
        data = copy.deepcopy(policy_data)
        if change:
            change(data)
        return Policy(data)
    return build


@pytest.fixture(scope="session")
def pipeline():
    """
    The notebook's main steps, run once on the files in data/.
    """
    importer = CsvImport()
    kb = importer.load_dir_data(ROOT / "data" / "kb")
    data = importer.load_dir_data(ROOT / "data" / "user")
    policy = Policy.load(POLICY_FILE, treatment_type_rows=kb["treatment_type"]["rows"])
    as_of = GeneratorSettings().as_of

    builder = FeatureBuilder(data, kb, as_of=as_of, default_dpd=90, outcome_months=6)
    rows = builder.training_set()
    model = LogisticPdModel(FeatureBuilder.numeric, FeatureBuilder.categorical).fit(rows)

    profiler = Profiler(policy, model, builder, data)
    portfolio = profiler.portfolio()
    today = profiler.on(portfolio, as_of)

    run_at = datetime.combine(as_of + timedelta(days=1), time(9, 0))
    actions = DunningEngine(policy, data["contact"]["rows"]).propose(today, run_at)
    checker = ComplianceChecker(policy, data["contact_history"]["rows"], data["case"]["rows"], data["ptp"]["rows"])
    decisions = checker.check_all(actions)
    log = Log(today, data["customer"]["rows"], data["contact"]["rows"])
    log.record_all(checker.decisions)

    roll_rates = RollRateModel(policy).fit(data["case_snapshot"]["rows"])
    dashboard = DashboardData(portfolio, data, decisions, roll_rates)
    return SimpleNamespace(kb=kb, data=data, policy=policy, as_of=as_of, builder=builder, rows=rows, model=model,
                           portfolio=portfolio, today=today, run_at=run_at, actions=actions, checker=checker,
                           decisions=decisions, log=log, roll_rates=roll_rates, dashboard=dashboard)
