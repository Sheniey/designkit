
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

class Navigation(Enum):
    STAY = auto() # stay in the current menu
    ROOT = auto() # go back to the root menu
    BACK = auto() # go back to the previous menu
    EXIT = auto() # exit the menu system



type Action[C] = Callable[[C], Navigation | None]

@dataclass
class Endpoint[C]:
    id: str
    label: str
    action: Action[C]

    def execute(self, context: C) -> Navigation:
        result = self.action(context)
        return result or Navigation.STAY

    @property
    def display_name(self) -> str:
        return self.label or self.id



type Selector[C] = Callable[[Menu[C]], str]

@dataclass
class Menu[C]:
    id: str
    label: str
    selector: Selector[C]

    _parent: Menu[C] | None = field(default=None, repr=False)
    _choices: dict[str, Menu[C] | Endpoint[C]] = field(
        default_factory=dict,
        repr=False,
    )

    def add(
        self,
        node: Menu[C] | Endpoint[C],
    ) -> Menu[C]:
        if node.id in self._choices:
            raise ValueError(
                f'Ya existe una opción con id={node.id!r} '
                f'en el menú {self.id!r}'
            )

        if isinstance(node, Menu[C]):
            node._parent = self

        self._choices[node.id] = node
        return self

    def menu(
        self,
        id: str,
        label: str,
        selector: Selector[C],
    ) -> Menu[C]:
        menu = Menu(
            id=id,
            label=label,
            selector=selector,
        )

        self.add(menu)
        return menu

    def endpoint(
        self,
        id: str,
        label: str,
        action: Action[C],
    ) -> Menu[C]:
        self.add(
            Endpoint(
                id=id,
                label=label,
                action=action,
            )
        )

        return self

    def root(self, label: str) -> Menu[C]:
        self.endpoint(
            id='__root__',
            label=label,
            action=lambda _: Navigation.ROOT,
        )

        return self

    def back(self, label: str) -> Menu[C]:
        self.endpoint(
            id='__back__',
            label=label,
            action=lambda _: Navigation.BACK,
        )

        return self

    def exit(self, label: str = 'Salir') -> Menu[C]:
        self.endpoint(
            id='__exit__',
            label=label,
            action=lambda _: Navigation.EXIT,
        )

        return self

    def choice(
        self,
        id: str,
    ) -> Menu[C] | Endpoint[C]:
        try:
            return self._choices[id]
        except KeyError:
            raise ValueError(
                f'La opción {id!r} no existe '
                f'en el menú {self.id!r}'
            ) from None

    def select(self, context: C) -> str:
        return self.selector(self)

    @property
    def parent(self) -> Menu[C] | None:
        return self._parent

    @property
    def choices(self) -> tuple[Menu[C] | Endpoint[C], ...]:
        return tuple(self._choices.values())

    @property
    def display_name(self) -> str:
        return self.label or self.id


@dataclass
class MenuRouter[C]:
    root: Menu[C]

    def run(self, context: C) -> None:
        current = self.root

        while True:
            selected_id = current.select(context)
            selected = current.choice(selected_id)

            if isinstance(selected, Menu[C]):
                current = selected
                continue

            navigation = selected.execute(context)

            if navigation is Navigation.EXIT:
                return

            if navigation is Navigation.BACK:
                if current.parent is None:
                    return

                current = current.parent


