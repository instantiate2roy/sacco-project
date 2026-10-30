from .contact_rule import ContactRule


class CaseStatusRule(ContactRule):
    name = "Case status"

    def __init__(self, policy):
        self.blocked = set(policy.compliance["do_not_treat_case_statuses"])

    def check(self, action, history, case):
        if case["status"] in self.blocked:
            return self._block(f"case is {case['status']}")
        return self._allow()
