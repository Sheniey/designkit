
from dataclasses import dataclass
from designkit.structural.modal_driven.models import Policy
from typing import Callable

@dataclass
class Shall(Policy):
    contract: Callable[[], bool]

    def evaluate(self) -> bool:
        return self.contract()
