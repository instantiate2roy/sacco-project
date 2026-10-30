from .message_template import MessageTemplate

class ReferralTemplate(MessageTemplate):
    """
    A referral hands the case to someone outside the collections team; the customer isn't contacted.
    """

    status = "REFERRED"

    def __init__(self, channel: str, referred_to: str):
        self.channel = channel
        self.referred_to = referred_to

    def recipient(self, loan):
        return self.referred_to

    def render(self, loan):
        return (f"Refer loan {loan['account_no']} ({loan['customer']}) to {self.referred_to}: "
                f"{loan['dpd']} days overdue, UGX {loan['outstanding_balance']:,} outstanding.")