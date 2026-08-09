
from designkit.structural.modal_driven import (
    Actor, Action, ModalEngine, Can
)

engine = ModalEngine()

player = Actor(
    name="Arthur",

    capabilities={
        "open_door",
        "attack",
    },

    permissions={
        "open_door",
    },

    obligations={
        "open_door",
    },

    intentions={
        "open_door",
    },

    history={
        "attack",
    }
)

open_door = Action(
    "open_door",
    lambda: print("🚪 Door opened!")
)

attack = Action(
    "attack",
    lambda: print("⚔️ Attack!")
)

policy = Can(player, open_door)

engine.execute(policy, open_door)
