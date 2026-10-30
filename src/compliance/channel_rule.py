from .contact_rule import ContactRule


class _ChannelRule(ContactRule):
    """Shared set-up for the rules that limit one channel."""

    def __init__(self, policy):
        self.limits = policy.compliance["channels"]

    def _same_channel(self, action, history):
        return history[history["channel"] == action.treatment]
