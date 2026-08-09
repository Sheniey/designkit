
from dataclasses import dataclass
from random import random
from designkit.structural.modal_driven.models import Policy

@dataclass
class Might(Policy):
    probability: float

    def __post_init__(self):
        if not 0 <= self.probability <= 1:
            raise ValueError("Probability must be between 0 and 1.")

    def evaluate(self):
        return random.random() < self.probability
