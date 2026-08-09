
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Policy
from typing import Callable

@dataclass
class OughtTo(Policy):
    expectation: Callable[[], bool]

    def evaluate(self) -> bool:
        return self.expectation()
