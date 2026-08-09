
from dataclasses import dataclass
from typing import Callable
from designkit.structural.modal_driven.models import Policy

@dataclass
class Should(Policy):
    recommendation: Callable[[], bool]

    def evaluate(self) -> bool:
        return self.recommendation()
