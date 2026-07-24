
from designkit.structural.decorador.core import DecorableInfo
from designkit_utils.shared import console

def explain(element: type) -> None:
    is_decorator = hasattr(element, '__component__')
    if not hasattr(element, '__decorables__') or not is_decorator:
        raise TypeError(f"'{element.__name__}' is not a valid component/decorator class")
    
    component: type
    if is_decorator:
        component = getattr(element, '__component__')
        console.print(f'[black bold]Decorables for [/black bold][green]{component.__name__}[/green]:')
    else:
        component = element
        console.print(f'[black bold]Decorables for [/black bold][green]{component.__name__}[/green]:')

    decorables: list[tuple[str, DecorableInfo]] = list(getattr(component, '__decorables__').items())
    for name, info in decorables:
        console.print(f'  - [yellow]\[{"optional" if info.optional else "[bold]required[/bold]"}][/yellow] [magenta italic]{"[bold]async[/bold]" if info.async_ else "sync"}[/magenta italic] [blue]{name}[/blue]() -- [black italic]{"cached" if info.cache else "not cached"}, {"traced" if info.trace else "not traced"}, {"locked" if info.lock else "not locked"}[/black italic]')
