
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Policy, Actor, Action

@dataclass
class Will(Policy):
    actor: Actor
    action: Action

    def evaluate(self) -> bool:
        return self.actor.intends(self.action)
