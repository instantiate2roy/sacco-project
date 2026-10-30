from .message_template import MessageTemplate

class EmailTemplate(MessageTemplate):
    channel = "EMAIL"

    def recipient(self, loan):
        return loan["email"]

    def render(self, loan):
        return (f"Subject: Loan {loan['account_no']} is overdue\n\n"
                f"Dear {loan['given_name']},\n\nYour loan {loan['account_no']} is {loan['dpd']} days overdue, "
                f"with UGX {loan['arrears_amount']:,} in arrears and UGX {loan['outstanding_balance']:,} "
                f"outstanding. Please pay the arrears, or contact your loan officer to agree a plan.")