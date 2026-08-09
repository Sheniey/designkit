
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Policy, Actor, Action
from typing import Callable

@dataclass
class Could(Policy):
    actor: Actor
    action: Action
    potential: Callable[[], bool] | None = None

    def evaluate(self):
        if not self.actor.can_do(self.action):
            return False

        if self.potential is None:
            return True

        return self.potential()
