
from typing import Any, Callable
from abc import ABC, abstractmethod

class TemplateMethod(ABC):
    @abstractmethod
    def run(self) -> None: ...

    def __str__(self) -> str:
        return f"{self.__class__.__name__} Template Method"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __call__(self) -> None:
        self.run()

def workflow(cls: Callable[..., Any]) -> Callable[..., Any]:
    def run(self) -> None:
        if not ( hasattr(self, "steps"), hasattr(self, "_steps") ):
            raise AttributeError(
                "Class must define 'steps'"
            )

        for step_name in getattr(self, "steps", getattr(self, "_steps", [])):
            method = getattr(self, step_name)
            method()

    cls = type(cls.__name__, (cls, TemplateMethod), dict(cls.__dict__))
    cls.run = run
    return cls

class Template(TemplateMethod, ABC):
    def run(self, *args: Any, **kwargs: Any) -> None:
        self.before(*args, **kwargs)
        self.process(*args, **kwargs)
        self.after(*args, **kwargs)

    def before(self, *args: Any, **kwargs: Any) -> None: ...

    @abstractmethod
    def process(self, *args: Any, **kwargs: Any) -> None: ...

    def after(self, *args: Any, **kwargs: Any) -> None: ...
