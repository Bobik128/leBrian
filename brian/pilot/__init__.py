from brian.pilot.Pilot import Pilot


class PilotException(Exception):
    """Base exception for pilot operations."""


class PilotAlreadyClosedError(PilotException):
    """Raised when trying to operate on a closed Pilot instance."""


PilotAlreadyClosedException = PilotAlreadyClosedError
"""Alias of PilotAlreadyClosedError for code that prefers the *Exception suffix."""


class PilotNotReadyError(PilotException):
    """Raised when trying to operate the pilot and it is not ready (e.g. motors not ready)."""


class PilotConfigurationError(PilotException):
    """Raised when pilot configuration is invalid (e.g. bad wheelbase or motor setup)."""


class PilotAlreadyReservedError(PilotException):
    """Raised when trying to create a pilot while PilotSync ownership is already reserved."""
