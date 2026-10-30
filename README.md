# SACCO loan risk profiling and collections

A Python system that helps a SACCO (Savings and Credit Cooperative Organisation) spot risky
borrowers early and organise how it collects overdue loans. It scores each loan's probability of
default (PD), groups overdue loans into delinquency buckets, chooses a collection treatment for each
one, checks every contact against the SACCO's contact rules, and shows the results on an interactive
dashboard with a 3 to 12 month loss projection.

The notebook `sacco.ipynb` is the user interface. The logic lives in classes under `src/`, and the
tests in `tests/` check those classes on their own and on the full data set.

The data is synthetic: about 1,200 members borrowing from October 2024 to the business date,
22 October 2026. Real SACCO data is private.

## Setting up

You need Python 3.10 or later.

```bash
python3 -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the notebook

1. Open `sacco.ipynb` in Jupyter or VS Code and pick the Python environment you installed into.
2. Restart the kernel, then run all cells from the top. Later cells use results from earlier ones.

Every list has its own filters and paging. The dashboard has one set of filters at the top
that every dashboard section follows, and an export cell that saves the filtered view as CSV
files or a PDF report in `export/<business date>/`.

The notebook reloads changed code in `src/` automatically, but not every change. If a cell fails
with an `ImportError` or an old class after you edit `src/`, restart the kernel and run all cells
again.

## Running the tests

From the project folder:

```bash
pytest
```

The suite takes about 20 seconds. The unit tests use small hand-made data, so each rule can be
checked exactly: CSV import, the policy checks, each compliance rule, dunning and its fallbacks,
the message templates, the risk models, the list and dashboard classes and the exporters. The
integration tests in `tests/test_pipeline.py` and `tests/test_dashboard.py` run the notebook's
steps once on the files in `data/` and check the results against the policy.

## Project layout

```
sacco.ipynb               the notebook
data/
  kb/                     reference data: loan, contact, treatment and other types, statuses, locations
  user/                   the SACCO's records: customers, loans, monthly snapshots, payments,
                          promises to pay, contacts and treatments
  configs/policy.json     the collection rules: buckets, risk tiers, profiles, treatments, contact limits
  models/                 the trained PD model the notebook saves
src/
  csv_import.py           CsvImport: reads and checks the CSV files
  synthetic_core_banking.py  SyntheticCoreBanking: generates the files in data/user
  policy.py               Policy: loads and checks policy.json, and answers bucket, tier and profile questions
  profiler.py             Profiler: gives every open loan a bucket, PD, risk tier and profile
  dunning.py              DunningEngine: proposes a treatment for each overdue loan
  exceptions.py           errors shared across the system
  risk/                   FeatureBuilder, LogisticPdModel (PD per loan), RollRateModel (projection)
  compliance/             one class per contact rule, and ComplianceChecker, which runs them in order
  notification/           message templates per channel, and Log, the record of every message
  display/                the searchable lists shown in the notebook
  plot/                   charts for the risk model
  dashboard/              DashboardData, the shared filters, the dashboard sections, their charts and the exporters
tests/                    pytest tests for everything in src/
```

Each package in `src/` keeps one class per file and exports its classes from `__init__.py`. A
package that raises errors of its own defines them in its `error.py`; `exceptions.py` holds the
errors the whole system shares.

## Data and rules

The files in `data/user` come from `SyntheticCoreBanking` with a fixed seed, so rebuilding them
gives the same files. To rebuild them, set `regenerate_banking_data = True` in the "Generate
synthetic data" cell and run it.

The collection rules are in `data/configs/policy.json`, not in the code. Change a bucket edge,
a contact limit or a treatment there and rerun the notebook. The policy is checked when it
loads, so a gap between buckets, an unknown treatment or a daily limit above the weekly one
stops the notebook with a message saying what is wrong.

## AI usage

An AI assistant (Claude, used through Claude Code) helped with five parts of this project:

| Area | What the AI did |
|---|---|
| README | Drafted this README from the code, the data files and the notebook. |
| Code review | Reviewed the classes in `src/` and pointed out problems. One example: the dashboard's export button caught `SaccoError`, which the export error does not inherit from, so a failed export would have stopped the dashboard instead of showing a message. |
| Tests | Wrote the pytest suite in `tests/`: unit tests on small hand-made data, and end-to-end tests that run the notebook's steps on the files in `data/`. |
| Debugging | Found and fixed the cause of several errors: a circular import in `src/notification`, imports of `ModelError` and `ExportError` from `exceptions.py` after they had moved or before they existed, `DunningEngine` failing on an empty contact list, and an `ImportError` in the notebook caused by a kernel that had loaded `src.display` before it had an `__init__.py`. |
| Proofing the notebook | Checked every markdown explanation against the code and a fresh run of the notebook: the AUC figures, the default rate in each score band, the back-test percentages, class names, file paths and the filters each list offers. Explanations that no longer matched were corrected. |

Each change was checked by running the notebook from the top and, once the tests existed, by
running the test suite.
