"""Identity and permissions (R4, R5).

Identity is the OS user, fetched automatically and never asked (Part 5). The
identity source is recorded so a self-declared or weak attribution is never
mistaken for strong identity (SDD §9).
"""

import getpass
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """A resolved user, with the source of the identity recorded."""

    user_id: str
    username: str
    identity_source: str = "os"


def current_user() -> User:
    """Resolve the current OS user without asking.

    Returns:
        A User whose identity_source is "os".
    """
    username = getpass.getuser()
    return User(user_id=username, username=username, identity_source="os")