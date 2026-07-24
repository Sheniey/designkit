
from typing import Callable
from .models import Policy


class PolicyException(Exception):
    """Base class for policy-related exceptions."""
    pass


class PolicyViolationError(PolicyException):
    """Exception raised when a policy is violated."""

    def __init__(self, policy: Callable[..., None] | Policy) -> None:
        name: str
        reason: str
        if isinstance(policy, Policy):
            name = policy.__class__.__name__
            reason = policy.violated_if
        else:
            name = policy.__name__
            reason = getattr(policy, 'violated_if', '<unknown violation condition> -- use a Policy class instead of perhaps a function')

        super().__init__(f"(Policy Violation) {name}(...) it's violated when {reason}")
        self.policy = policy
        self.policy_name = name
        self.violation_reason = reason

class InvalidPolicyError(PolicyException):
    """Exception raised when an invalid policy is provided."""

    def __init__(self, policy: Callable[..., None] | Policy) -> None:
        name: str
        if isinstance(policy, Policy):
            name = policy.__class__.__name__
        else:
            name = policy.__name__

        super().__init__(f'An invalid policy was provided: {name}(...)')
        self.policy = policy
        self.policy_name = name
