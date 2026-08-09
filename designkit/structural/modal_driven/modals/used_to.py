
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Policy, Actor, Action

@dataclass
class UsedTo(Policy):
    actor: Actor
    action: Action

    def evaluate(self) -> bool:
        return self.actor.used_to_do(self.action)
