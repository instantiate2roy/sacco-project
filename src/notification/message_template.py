from abc import ABC, abstractmethod

class MessageTemplate(ABC):
    """
    How one channel addresses and words a message about an overdue loan.
    """

    channel: str = ""
    status: str = "SENT"            # what an allowed message becomes

    @abstractmethod
    def recipient(self, loan: dict) -> str:
        """
        Who the message goes to.
        """

    @abstractmethod
    def render(self, loan: dict) -> str:
        """
        The message text, from the loan's details (account_no, given_name, dpd, arrears_amount, ...).
        """
