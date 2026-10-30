from .message_template import MessageTemplate

class SmsTemplate(MessageTemplate):
    channel = "SMS"

    def recipient(self, loan):
        return loan["mobile"]

    def render(self, loan):
        return (f"Dear {loan['given_name']}, your loan {loan['account_no']} is {loan['dpd']} days overdue. "
                f"Please pay UGX {loan['arrears_amount']:,} to bring it up to date, or call us if you need help.")