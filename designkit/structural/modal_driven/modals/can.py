
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Policy, Actor, Action

@dataclass
class Can(Policy):
    actor: Actor
    action: Action

    def evaluate(self):
        return self.actor.can_do(self.action)
