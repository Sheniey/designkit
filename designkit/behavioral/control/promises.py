
from typing import Any, Callable, TypedDict
from dataclasses import dataclass, field
import multiprocessing as mp

# ==================================================
# Types
# ==================================================

class ProcessAsDict[T, A, K](TypedDict):
    func: Callable[..., T]
    args: list[A] | None
    kwargs: dict[str, K] | None

type ProcessAsTuple[T, A, K] = tuple[Callable[..., T], list[A], dict[str, K]]

# ==================================================
# Promise/Task States
# ==================================================

@dataclass(frozen=True)
class Pending:
    pass

@dataclass(frozen=True)
class Resolved[T]:
    __match_args__ = ('value',)
    value: T

@dataclass(frozen=True)
class Rejected[E]:
    __match_args__ = ('error',)
    error: E



# ==================================================
# Type Aliases
# ==================================================

type FutureState[T, E] = (
    Pending
    | Resolved[T]
    | Rejected[E]
)



# ==================================================
# Abstact Base Classes
# ==================================================

@dataclass
class Future[T, E]:
    state: FutureState[T, E] = field(default_factory=Pending)

    @property
    def settled(self) -> bool:
        return not isinstance(self.state, Pending)



# ==================================================
# Concrete Implementations
# ==================================================

@dataclass
class Promise[T, E](Future[T, E]):
    def resolve(self, value: T) -> None:
        if self.settled:
            raise RuntimeError('Cannot resolve a Promise that is already settled.')
        
        self.state = Resolved(value)
        
    def reject(self, error: E) -> None:
        if self.settled:
            raise RuntimeError('Cannot reject a Promise that is already settled.')
        
        self.state = Rejected(error)

@dataclass
class Task[T, E](Future[T, E]):
    def run(
            self,
            processes: list[ProcessAsDict[T, Any, Any] | ProcessAsTuple[T, Any, Any]],
            *,
            workers: int = 1,
        ) -> None:

        if self.settled:
            raise RuntimeError('Cannot run a Task that is already settled.')
        
        _normalized_processes: list[ProcessAsTuple[T, Any, Any]] = []
        for process in processes:
            if isinstance(process, dict):
                func = process['func']
                args = process.get('args', [])
                kwargs = process.get('kwargs', {})
                _normalized_processes.append((func, args, kwargs))
            elif isinstance(process, tuple) and len(process) == 3:
                _normalized_processes.append(process)
            else:
                raise ValueError('Each process must be either a dict or a tuple of (func, args, kwargs).')

        workers: int = min(workers, mp.cpu_count())
        try:
            with mp.Pool(processes=workers) as pool:
                mapped_results = [
                    pool.apply_async(func, args=args, kwds=kwargs)
                    for func, args, kwargs in _normalized_processes
                ]
            results = [r.get() for r in mapped_results]
            self.state = Resolved(results)
        except Exception as e:
            self.state = Rejected(e)
            raise e
