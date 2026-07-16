class IllegalStateTransition(ValueError):
    """Raised when an operation is not permitted by the Battle state machine."""


_ALLOWED_TRANSITIONS = {
    "created": {"answering"},
    "answering": {"ready", "aborted"},
    "ready": {"voted"},
    "voted": {"scored"},
    "aborted": set(),
    "scored": set(),
}


def transition(current: str, target: str) -> str:
    if target not in _ALLOWED_TRANSITIONS.get(current, set()):
        raise IllegalStateTransition(f"cannot transition from {current} to {target}")
    return target
