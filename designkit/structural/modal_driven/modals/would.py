
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Policy, Action
from typing import Callable

@dataclass
class Would(Policy):
    condition: Callable[[], bool]
    action: Action

    def evaluate(self) -> bool:
        if self.condition():
            return True

        return False
