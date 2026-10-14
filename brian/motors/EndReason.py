from enum import Enum
class EndReason(Enum):
    """
    Reasons for movement end.
    """

    FINISHED = 0
    """Movement finished"""
    TIMED_OUT = 1
    """Timed out"""
