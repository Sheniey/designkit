
from typing import Any, Self

from .exceptions import (
    PolicyViolationError, InvalidPolicyError
)
from .models import Policy


class CompositePolicy:
    __slots__ = ('policies',)

    def __init__(self, policies: list[Policy]) -> None:
        for policy in policies:
            if not CompositePolicy.is_valid_policy(policy):
                raise InvalidPolicyError(policy)

        self.policies = policies

    def __call__(self, *args, **kwargs) -> Self:
        return self.apply(*args, **kwargs)

    def __repr__(self) -> str:
        fn_policy_names = [policy.__name__ for policy in self.policies]
        cls_policy_names = [policy.__class__.__name__ for policy in self.policies]
        return f"{self.__class__.__name__}( {', '.join(fn_policy_names + cls_policy_names)} )"

    def __rlshift__(
            self,
            other: Any | tuple[list[Any], dict[str, Any]] | Policy
        ) -> None:
    
        match other:
            # 5 >> IntegerPolicy() >> NonZeroNumberPolicy()
            case Policy():
                if other.___latest_data is not None:
                    args, kwargs = other.___latest_data
                    self(*args, **kwargs)
            # (5, ...) >> NonZeroNumberPolicy()
            case (list() as args, dict() as kwargs):
                self(*args, **kwargs)
            # 5 >> NonZeroNumberPolicy()
            case _:
                self(other)

    def __add__(self, other: Policy) -> CompositePolicy:
        if not CompositePolicy.is_valid_policy(other):
            raise InvalidPolicyError(other)

        return CompositePolicy(self.policies + [other])

    def __radd__(self, other: Policy) -> CompositePolicy:
        return self.__add__(other)

    def __iadd__(self, other: Policy) -> Self:
        return self.add_policy(other)

    def __isub__(self, other: Policy) -> Self:
        return self.remove_policy(other)

    @staticmethod
    def is_valid_policy(policy: Any) -> bool:
        return callable(policy) and isinstance(policy, Policy)

    def add_policy(self, policy: Policy) -> Self:
        if not CompositePolicy.is_valid_policy(policy):
            raise InvalidPolicyError(policy)

        self.policies.append(policy)
        return self

    def remove_policy(self, policy: Policy) -> Self:
        if policy in self.policies:
            self.policies.remove(policy)
        return self

    def apply(self, *args, **kwargs) -> Self:
        for policy in self.policies:
            try:
                policy(*args, **kwargs)
            except Exception as e:
                raise PolicyViolationError(policy) from e

        return self


def apply_policies(policies: list[Policy], *args, **kwargs) -> None:
    for policy in policies:
        policy(*args, **kwargs)


# Example usage:

def positive_number(number: int) -> None:
    if number < 0:
        raise ValueError("Number must be positive")

def integer_number(number: int) -> None:
    if not isinstance(number, int):
        raise ValueError("Number must be an integer")

class NonZeroNumberPolicy(Policy):
    violated_if = 'A number provided is zero.'

    def apply(self, number: int) -> None:
        if number == 0:
            raise ValueError("Number must be non-zero")

apply_policies(
    [positive_number, integer_number, NonZeroNumberPolicy()],
    5
)
