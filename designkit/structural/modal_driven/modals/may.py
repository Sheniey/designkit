
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Action, Actor, Policy

@dataclass
class May(Policy):
    actor: Actor
    action: Action

    def evaluate(self) -> bool:
        return self.actor.may_do(self.action)
