
from designkit.structural.modal_driven.models import Policy, Action

class ModalEngine:

    def check(self, policy: Policy) -> bool:
        return policy.evaluate()

    def execute(
        self,
        policy: Policy,
        action: Action
    ):
        if policy.evaluate():
            return action()

        return False
