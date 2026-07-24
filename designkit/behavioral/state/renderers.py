
from typing import Protocol
from enum import Enum

from .fsm_types import StateMachinePayload, RequiredParts
from .tools import console

class Renderer[S: Enum, E: Enum, C](Protocol):
    requires: RequiredParts
    def render(self, payload: StateMachinePayload[S, E, C]) -> None: ...

class LinkRenderer[S: Enum, E: Enum, C](Renderer[S, E, C]):
    requires: RequiredParts = 'transitions'

    def render(self, payload: StateMachinePayload[S, E, C]) -> None:
        for (state, event), (next_state, _, guard) in payload.get('transitions', {}).items():
            console.print(f'   [magenta]<[/magenta][green]{state.name}[/green][magenta]> ==[/magenta][yellow]{event.name}[/yellow][magenta]==> <[/magenta][green]{next_state.name}[/green][magenta]> : [/magenta][cyan]{guard.__name__ if guard else "always_true"}[/cyan]()')

class JSONRenderer[S: Enum, E: Enum, C](Renderer[S, E, C]):
    requires: RequiredParts = 'any'
    def __init__(self, indent: int = 4): self.__indent = indent
    
    def render_transitions(self, payload: StateMachinePayload[S, E, C]) -> None:
        formatted_transitions: list[dict[str, str]] = []
        for (state, event), (next_state, func, guard) in payload.get('transitions', {}).items():
            formatted_transitions.append({
                'from': state.name,
                'event': event.name,
                'to': next_state.name,
                'action': f'{func.__name__}()',
                'guard': f'{guard.__name__}()' if guard else 'always_true()'
            })
        console.print_json(data=formatted_transitions, indent=self.__indent)

    def render_hooks(self, payload: StateMachinePayload[S, E, C]) -> None:
        formatted_hooks: dict[str, dict[str, list[str]]] = {}

        enter_, exit_ = payload.get('hooks', {}).get('on_enter', {}), payload.get('hooks', {}).get('on_exit', {})
        before, after = payload.get('hooks', {}).get('before_each_transition', []), payload.get('hooks', {}).get('after_each_transition', [])
        
        formatted_hooks['global_hooks'] = {
            'before_each_transition': [f'{hook.__name__}()' for hook in before],
            'after_each_transition': [f'{hook.__name__}()' for hook in after]
        }
        formatted_hooks['on_enter'] = [
            {
                'state': state.name,
                'hooks': [f'{hook.__name__}()' for hook in hooks]
            } for state, hooks in enter_.items()
        ]
        formatted_hooks['on_exit'] = [
            {
               'state': state.name,
                'hooks': [f'{hook.__name__}()' for hook in hooks]
            } for state, hooks in exit_.items()
        ]

        console.print_json(data=formatted_hooks, indent=self.__indent)

    def render_both(self, payload: StateMachinePayload[S, E, C]) -> None:
        formatted_transitions: list[dict[str, str]] = []
        formatted_hooks: dict[str, dict[str, list[str]]] = {}
        transitions = payload.get('transitions', {})
        hooks = payload.get('hooks', {})

        print(payload)
        enter_, exit_ = hooks.get('on_enter', {}), hooks.get('on_exit', {})
        before, after = hooks.get('before_each_transition', []), hooks.get('after_each_transition', [])

        formatted_hooks['before_each_transition'] = [f'{hook.__name__}()' for hook in before]
        formatted_hooks['after_each_transition'] = [f'{hook.__name__}()' for hook in after]

        for (state, event), (next_state, func, guard) in transitions.items():
            formatted_transitions.append({
                'from': state.name,
                'event': event.name,
                'to': next_state.name,
                'action': f'{func.__name__}()',
                'guard': f'{guard.__name__}()' if guard else 'always_true()',
                'hooks': {
                    'on_enter': [f'{hook.__name__}()' for hook in enter_.get(state, [])],
                    'on_exit': [f'{hook.__name__}()' for hook in exit_.get(state, [])]
                }
            })
            
        console.print_json(data={
            'global_hooks': formatted_hooks,
            'transitions': formatted_transitions
        }, indent=self.__indent)

    def render(self, payload: StateMachinePayload[S, E, C]) -> None:
        hooks_enabled, trans_enabled = bool(payload.get('hooks')), bool(payload.get('transitions'))

        if trans_enabled and not hooks_enabled: self.render_transitions(payload)
        if not trans_enabled and hooks_enabled: self.render_hooks(payload)
        if trans_enabled and hooks_enabled: self.render_both(payload)
