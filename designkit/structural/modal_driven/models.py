
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Callable, Any


@dataclass(frozen=True)
class Action:
    name: str
    execute: Callable[..., Any]

    def __call__(self, *args, **kwargs):
        return self.execute(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name!r})'

@dataclass
class Actor:
    name: str

    capabilities: set[str] = field(default_factory=set)
    permissions: set[str] = field(default_factory=set)
    obligations: set[str] = field(default_factory=set)

    intentions: set[str] = field(default_factory=set)
    history: set[str] = field(default_factory=set)

    def can_do(self, action: Action) -> bool:
        return action.name in self.capabilities

    def may_do(self, action: Action) -> bool:
        return action.name in self.permissions

    def must_do(self, action: Action) -> bool:
        return action.name in self.obligations

    def intends(self, action: Action) -> bool:
        return action.name in self.intentions

    def used_to_do(self, action: Action) -> bool:
        return action.name in self.history

class Policy(ABC):
    def __str__(self):
        return self.explain()

    def __bool__(self):
        return self.evaluate()

    def __and__(self, other: Policy) -> Policy:
        return AllOf(self, other)

    def __or__(self, other: Policy) -> Policy:
        return AnyOf(self, other)

    def __xor__(self, other: Policy) -> Policy:
        return AnyOf(AllOf(self, Not(other)), AllOf(Not(self), other))

    def __invert__(self) -> Policy:
        return Not(self)

    def __pos__(self) -> Policy:
        return self

    def __neg__(self) -> Policy:
        return Not(self)

    @abstractmethod
    def evaluate(self) -> bool:
        ...

    # @abstractmethod
    def explain(self) -> str:
        ...

    def if_(self, condition: Policy) -> Policy:
        return Conditional(condition, self)

    def when_(self, condition: Policy) -> Policy:
        return Conditional(condition, self)


@dataclass
class AllOf(Policy):
    policies: tuple[Policy, ...]

    def __init__(self, *policies) -> None:
        self.policies = policies

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(repr(p) for p in self.policies)})'

    def evaluate(self) -> bool:
        return all(policy.evaluate() for policy in self.policies)


@dataclass
class AnyOf(Policy):
    policies: tuple[Policy, ...]

    def __init__(self, *policies) -> None:
        self.policies = policies

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(repr(p) for p in self.policies)})'

    def evaluate(self) -> bool:
        return any(policy.evaluate() for policy in self.policies)


@dataclass
class Not(Policy):
    policy: Policy

    def evaluate(self) -> bool:
        return not self.policy.evaluate()


@dataclass
class Conditional(Policy):
    condition: Policy
    policy: Policy

    def evaluate(self) -> bool:
        if self.condition.evaluate():
            return self.policy.evaluate()

        return True
