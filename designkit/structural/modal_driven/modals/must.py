
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Actor, Action, Policy

@dataclass
class Must(Policy):
    actor: Actor
    action: Action

    def evaluate(self) -> bool:
        return self.actor.must_do(self.action)