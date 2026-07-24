
from typing import Any, Callable, Final as Const


class PipelineError(Exception):
    pass

class TaskSequenceError(Exception):
    pass

STOP_ITERATION: Const[str] = "There are no more steps to process... reset the sequence to start over."

class TaskRegistrationError(PipelineError, TaskSequenceError):
    def __init__(self, func: Any) -> None:
        self.func = func
        super().__init__(f"Invalid task function: {func} is not a valid function to register as a task.")

class InvalidReturnedValueError(PipelineError, TaskSequenceError):
    def __init__(self, func: Callable[..., Any], expected: str, positional_index: int) -> None:
        super().__init__(f"Invalid returned value: The {positional_index} returned value from task {func.__name__}() is not valid. Expected: {expected}.")

class NothingWasReturnedError(TaskSequenceError):
    def __init__(self, func: Callable[..., Any]) -> None:
        super().__init__(f"Nothing was returned: Task {func.__name__}() did not return any value or None, but a value is expected.")
