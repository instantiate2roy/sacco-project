from .message_template import MessageTemplate

class CallTemplate(MessageTemplate):
    """
    A call is queued for an officer to make, with a note of what to discuss.
    """

    channel = "CALL"
    status = "QUEUED"

    def recipient(self, loan):
        return loan["mobile"]

    def render(self, loan):
        return (f"Call {loan['customer']} about loan {loan['account_no']}: {loan['dpd']} days overdue, "
                f"UGX {loan['arrears_amount']:,} in arrears. Ask for payment or a promise to pay.")