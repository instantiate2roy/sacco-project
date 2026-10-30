class SaccoError(Exception):
    """Base class for every error raised by the SACCO collection system."""
 
class ImportFileError(SaccoError):
    """An import file is missing, unreadable, empty or badly formed."""

class PolicyError(SaccoError):
    """configs/policy.json is missing, or one of its rules is incomplete or contradicts another."""