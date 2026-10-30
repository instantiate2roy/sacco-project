"""
The compliance rules a proposed treatment must pass before it is carried out.

Each rule is a ContactRule with one method, check(), which says whether the action is allowed
and, if not, why. The limits themselves come from the policy file, so the rules only hold logic.
"""
from abc import ABC, abstractmethod

import pandas as pd

from .proposed_action import ProposedAction
from .rule_outcome import RuleOutcome

# treatments that contact the customer directly; referrals (DCA, LEGAL) don't
CONTACT_CHANNELS = {"SMS", "EMAIL", "CALL"}


class ContactRule(ABC):
    """One compliance rule. Subclasses read their limits from the policy in __init__."""

    name: str = "rule"

    @abstractmethod
    def check(self, action: ProposedAction, history: pd.DataFrame, case: dict) -> RuleOutcome:
        """
        history: the customer's past contacts (columns contact_datetime, channel), newest last.
        case: the case's current details (status, pending promise, ...).
        """

    def _allow(self) -> RuleOutcome:
        return RuleOutcome(self.name, True)

    def _block(self, reason: str) -> RuleOutcome:
        return RuleOutcome(self.name, False, reason)
