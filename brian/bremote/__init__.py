from brian.bremote.BRemote import BRemote


class BRemoteDisconnectedError(Exception):
    """Thrown when a BRemote disconnects while a blocking wait is in progress."""


def list() -> list[BRemote]:
    """
    :return: Connected and reconnecting BRemote instances currently visible to programs.
    Pairing and discovered-only remotes are not included.
    """
    ...
