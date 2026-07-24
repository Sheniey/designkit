
from dataclasses import dataclass, field
from typing import Any, Callable, Final as Const
import hashlib, random, inspect
from designkit_utils.extras import IDENT
from designkit_utils.symbols import SUCCESS_SYMBOL, PENDING_SYMBOL, ERROR_SYMBOL
from designkit_utils.generators import uuid

from .exceptions import (
    STOP_ITERATION,
    InvalidReturnedValueError,
    PipelineError,
    TaskRegistrationError,
    TaskSequenceError,
)



OK_STATUS: Const[int] = 0
FAIL_STATUS: Const[int] = 1
PENDING_STATUS: Const[int] = 2


@dataclass
class Pipeline[F: Callable[..., Any]]:
    """
    *"Makes a linked execution pipeline."*

    The `Pipeline` class allows you to create a sequence
    of tasks (functions) that can be executed in order.
    Each task can return values that will be passed as arguments
    to the next task in the sequence. 
    You can also set an initial state for the pipeline,
    which will be used as the input for the first task.

    *Every instance of this class has a unique identifier generated using the `uuid` function.*

    Attributes:
        ignore_exceptions(bool): If set to True, the pipeline will ignore exceptions raised by tasks and continue execution.
        loops(int): The number of times the pipeline has completed a full cycle through its tasks.
        arguments(tuple[list[Any], dict[str, Any]]): The current arguments (positional and keyword) that will be passed to the next task when `walk` is called.
        current_step(int): The index of the next task to be executed (1-based).
        total_steps(int): The total number of tasks registered in the pipeline.
        remaining_steps(int): The number of tasks that have not yet been executed in the current cycle
    """

    _ignore_exceptions: bool = False

    id: int = field(default_factory=uuid, init=False)
    tasks: list[F] = field(default_factory=list)
    
    next_args: list[Any] = field(default_factory=list)
    next_kwargs: dict[str, Any] = field(default_factory=dict)

    __index: int = field(default=0, init=False, repr=False)
    __loops: int = field(default=0, init=False, repr=False)
    __status: list[int] = field(default_factory=list, init=False, repr=False)
    
    # ==================================================
    # Representation
    # ==================================================

    def __str__(self) -> str:
        symbol_map: dict[int, str] = {
            OK_STATUS: SUCCESS_SYMBOL,
            FAIL_STATUS: ERROR_SYMBOL,
            PENDING_STATUS: PENDING_SYMBOL,
        }
        output: str = ''

        for step, status in enumerate(self.__status):
            marker: str = symbol_map.get(status, PENDING_SYMBOL)
            output += f'{IDENT}{marker} Step {step + 1}\n'
        
        return (
            f'{self.__class__.__name__}:\n'
            f'{output}'
        )
    
    def __repr__(self) -> str:
        func_reprs: str = "\n".join(
            f'{IDENT*2}' f'{step}: {func.__name__}(...);'
            for step, func in enumerate(self.tasks)
        )
        return (
            f'{self.__class__.__name__}(\n'
            f'{IDENT}' f'id:"{self.id}",\n'
            f'{IDENT}' f'steps:"{len(self)}",\n'
            f'{IDENT}' f'loops:{self.__loops},\n'
            f'{IDENT}' f'task_flow:\n'
            f'{func_reprs}'
            f'\n)'
        )


    # ==================================================
    # Meta Methods
    # ==================================================

    def __len__(self) -> int:
        """
        *"Returns the total number of tasks registered in the pipeline."*
        """
        return len(self.tasks)


    # ==================================================
    # Utilities
    # ==================================================

    def reset(self) -> None:
        """
        *"Resets the pipeline to its initial state."*

        This method resets the internal index to zero
        and clears the next arguments and keyword arguments.
        Use `set_initial_state` to set the initial arguments
        for the first task after resetting.
        """

        self.__index = 0
        self.__status.clear()
        self.next_args, self.next_kwargs = [], {}

    def set_initial_state(self, *args: Any, **kwargs: Any) -> None:
        """
        *"Sets the initial state for the pipeline."*

        This method sets the initial arguments and keyword arguments
        that will be passed to the first task when the pipeline starts.

        Args:
            *args: Positional arguments to be passed to the first task.
            **kwargs: Keyword arguments to be passed to the first task.
        """

        self.next_args = list(args)
        self.next_kwargs = dict(kwargs)


    # ==================================================
    # Registration
    # ==================================================

    def task(self, func: F) -> F:
        """
        *"Registers a task (function) to the pipeline."*

        This method takes a callable (function)
        as an argument and adds it to the pipeline's tasks.
        The registered function should accept the arguments
        that will be passed from the previous task in the pipeline.

        Args:
            func: A callable (function) to be registered as a task in the pipeline.
        
        Returns:
            The same function that was registered, allowing for decorator usage.
        """

        if not callable(func):
            raise TaskRegistrationError(func)
        self.tasks.append(func)
        return func
    

    # ==================================================
    # Execution
    # ==================================================
    
    def _prepare_execution(self) -> tuple[F, list[Any], dict[str, Any]]:
        """
        *"Prepares the next task for execution."*

        A `protected` internal function that retrieves the next task
        to be executed along with the arguments that will be passed to it.
        If the end of the pipeline is reached, a `StopIteration` exception is raised here.

        Returns:
            tuple[F, list[Any], dict[str, Any]]: A tuple containing the task function, *args, and **kwargs.

        Raises:
            StopIteration: If the end of the pipeline is reached.
        """

        if self.__index >= self.total_steps:
            self.__loops += 1
            raise StopIteration(STOP_ITERATION)

        task: F = self.tasks[self.__index]
        args, kwargs = self.next_args, self.next_kwargs
        return task, args, kwargs

    def _process_result(self, func: F, result: Any) -> None:
        """
        *"Processes the result returned by a task."*

        A `protected` internal function that takes the result returned by a task
        and updates the next arguments and keyword arguments
        that will be passed to the subsequent task in the pipeline.

        Args:
            func: The task function that produced the result.
            result: The result returned by the task function.

        Raises:
            InvalidReturnedValueError: If the result is not in the expected format (None or a tuple of (args, kwargs)).
        """

        if result is None:
            self.next_args = []
            self.next_kwargs = {}
                
        elif isinstance(result, tuple) and len(result) == 3:
            args, kwargs = result[0:2], result[2]

            if not isinstance(kwargs, dict):
                raise InvalidReturnedValueError(func, "dict as kwargs", 3)

            self.next_args = list(args)
            self.next_kwargs = kwargs

        else:
            self.next_args = [result]
            self.next_kwargs = {}

    def _finalize_execution(self, *, exception: Exception | None = None) -> None:
        """
        *"Finalizes the execution of a task."*

        A `protected` internal function that updates the pipeline's status based on the
        outcome of the task execution. If an exception occurred,
        it handles the exception according to the pipeline's settings.

        Args:
            exception: The exception raised during task execution, if any.
        """

        self.__index += 1

        if exception is not None:
            self.__status.append(FAIL_STATUS)

            if not self._ignore_exceptions:
                raise exception

            return

        self.__status.append(OK_STATUS)
    
    def _abort_pipeline(self) -> None:
        """
        *"Aborts the pipeline execution due to an invalid return value."*

        A `protected` internal function that is called when a task returns an invalid value.
        It marks the current task as failed and fills the remaining tasks with a failed status.
        """
        for _ in range(self.remaining_steps):
            self.__status.append(FAIL_STATUS)
            self.__index += 1
        self.__loops += 1

    def walk(self, steps: int = 1) -> None:
        """
        *"Executes a specified number of steps in the pipeline sync."*

        This method executes synchronously the tasks
        in the pipeline for the given number of steps.
        If the end of the pipeline is reached,
        a `StopIteration` exception is raised.

        Args:
            steps: The number of steps to execute. Defaults to 1.
        
        Raises:
            StopIteration: If the end of the pipeline is reached before completing the specified steps.
        """
        for _ in range(steps):
            func, args, kwargs = self._prepare_execution()
            try:
                result: Any = func(*args, **kwargs)

                self._process_result(func, result)
            except InvalidReturnedValueError:
                self._abort_pipeline()
                break
            except Exception as e:
                self._finalize_execution( exception=e )
            else:
                self._finalize_execution()
    
    async def walk_async(self, steps: int = 1) -> None:
        """
        *"Executes a specified number of steps in the pipeline async."*

        This method executes asynchronously the tasks
        in the pipeline for the given number of steps.
        If the end of the pipeline is reached,
        a `StopIteration` exception is raised.

        Args:
            steps: The number of steps to execute. Defaults to 1.
        
        Raises:
            StopIteration: If the end of the pipeline is reached before completing the specified steps.
        """

        for _ in range(steps):
            func, args, kwargs = self._prepare_execution()
            try:
                result: Any = func(*args, **kwargs)

                if inspect.isawaitable(result):
                    result = await result

                self._process_result(func, result)
            except InvalidReturnedValueError:
                self._abort_pipeline()
                break
            except Exception as e:
                self._finalize_execution( exception=e )
            else:
                self._finalize_execution()

    def run(self) -> None:
        """
        *"Executes the entire pipeline synchronously."*

        This method executes all the tasks in the
        pipeline synchronously until the end is reached.
        """

        while self.__index < len(self.tasks):
            self.walk()
        self.__loops += 1
    
    async def run_async(self) -> None:
        """
        *"Executes the entire pipeline asynchronously."*

        This method executes all the tasks in the pipeline
        asynchronously when needed until the end is reached.
        """

        while self.__index < len(self.tasks):
            await self.walk_async()
        self.__loops += 1


    # ==================================================
    # Properties
    # ==================================================

    @property
    def ignore_exceptions(self) -> bool:
        """
        *"Returns if ignore exceptions is enabled."*

        Returns:
            bool: True if the pipeline is set to ignore exceptions, False otherwise.
        """
        return self._ignore_exceptions

    @ignore_exceptions.setter
    def ignore_exceptions(self, value: bool) -> None:
        """
        *"Sets whether the pipeline should ignore exceptions during execution."*

        Args:
            value: A boolean indicating whether to ignore exceptions (True) or not (False).
        """
        self._ignore_exceptions = value

    @property
    def loops(self) -> int:
        """
        *"Returns the number of loops completed by the pipeline."*

        Returns:
            int: The number of loops completed.
        """
        return self.__loops
    
    @property
    def arguments(self) -> tuple[list[Any], dict[str, Any]]:
        """
        *"Returns the arguments that will be passed to the next task."*

        Returns:
            tuple[list[Any], dict[str, Any]]: The next arguments and keyword arguments.
        """
        return self.next_args, self.next_kwargs

    @property
    def current_step(self) -> int:
        """
        *"Returns the current step number in the pipeline."*

        Returns:
            int: The current step number.
        """
        return self.__index + 1
    
    @property
    def total_steps(self) -> int:
        """
        *"Returns the total number of steps in the pipeline."*

        Returns:
            int: The total number of steps.
        """
        return len(self.tasks)
    
    @property
    def remaining_steps(self) -> int:
        """
        *"Returns the number of remaining steps in the pipeline."*

        Returns:
            int: The number of remaining steps.
        """
        return len(self.tasks) - self.__index

@dataclass
class TaskSequence[F: Callable[..., None]]:
    """
    *"Executes a fixed sequence of tasks with predefined arguments."*

    The `TaskSequence` class allows you to register tasks
    along with their own positional and keyword arguments.
    Unlike `Pipeline`, tasks do not pass values between each other.
    Every task in the sequence must return `None`.

    *Every instance of this class has a unique identifier hashed from a random value.*

    Attributes:
        ignore_exceptions(bool): If set to True, the sequence will ignore exceptions raised by tasks and continue execution.
        loops(int): The number of times the sequence has completed a full cycle through its tasks.
        current_step(int): The index of the next task to be executed (1-based).
        total_steps(int): The total number of tasks registered in the sequence.
        remaining_steps(int): The number of tasks that have not yet been executed in the current cycle.
    """
    _ignore_exceptions: bool = False

    id: int = field(default_factory=uuid, init=False)
    tasks: list[tuple[F, list[Any], dict[str, Any]]] = field(default_factory=list)
    
    __index: int = field(default=0, init=False, repr=False)
    __loops: int = field(default=0, init=False, repr=False)
    __status: list[int] = field(default_factory=list, init=False, repr=False)

    # ==================================================
    # Representation
    # ==================================================

    def __str__(self) -> str:
        symbol_map: dict[int, str] = {
            FAIL_STATUS: ERROR_SYMBOL,
            PENDING_STATUS: PENDING_SYMBOL,
            OK_STATUS: SUCCESS_SYMBOL
        }
        output: str = ''

        for step, status in enumerate(self.__status):
            marker: str = symbol_map.get(status, PENDING_SYMBOL)
            output += f'{IDENT}{marker} Step {step + 1}\n'
        
        return (
            f'{self.__class__.__name__}:\n'
            f'{output}'
        )

    def __repr__(self) -> str:
        func_reprs: str = "\n".join(
            f'{IDENT*2}' f'{step+1}: {func.__name__}(...);'
            for step, (func, args, kwargs) in enumerate(self.tasks)
        )
        return (
            f'{self.__class__.__name__}(\n'
            f'{IDENT}' f'id:"{self.id}",\n'
            f'{IDENT}' f'steps:"{self.total_steps}",\n'
            f'{IDENT}' f'loops:{self.__loops},\n'
            f'{IDENT}' f'tasks:\n'
            f'{func_reprs}\n'
            f')'
        )


    # ==================================================
    # Meta Methods
    # ==================================================

    def __len__(self) -> int:
        """
        *"Returns the total number of tasks registered in the sequence."*
        """
        return self.total_steps


    # ==================================================
    # Utilities
    # ==================================================

    def reset(self) -> None:
        """
        *"Resets the sequence to its initial state."*

        This method resets the internal index to zero
        and clears all recorded step statuses.
        """
        self.__index = 0
        self.__status.clear()


    # ==================================================
    # Registration
    # ==================================================

    def task(self, *args: Any, **kwargs: Any) -> Callable[[F], F]:
        """
        *"Registers a task (function) to the sequence with fixed arguments."*

        This method returns a decorator that stores a callable
        together with the arguments that will always be used
        when that task is executed.

        Args:
            *args: Positional arguments to bind to the task.
            **kwargs: Keyword arguments to bind to the task.

        Returns:
            Callable[[F], F]: A decorator that registers the task.
        """

        def decorator(func: F) -> F:
            if not callable(func):
                raise TaskRegistrationError(func)
            self.tasks.append((func, list(args), dict(kwargs)))
            return func
        return decorator


    # ==================================================
    # Execution
    # ==================================================

    def _prepare_execution(self) -> tuple[F, list[Any], dict[str, Any]]:
        """
        *"Prepares the next task for execution."*

        A `protected` internal function that retrieves the next task
        to be executed along with its bound arguments.
        If the end of the sequence is reached, a `StopIteration` exception is raised.

        Returns:
            tuple[F, list[Any], dict[str, Any]]: A tuple containing the task function, *args, and **kwargs.

        Raises:
            StopIteration: If the end of the sequence is reached.
        """

        if self.__index >= self.total_steps:
            self.__loops += 1
            raise StopIteration(STOP_ITERATION)

        task, args, kwargs = self.tasks[self.__index]
        return task, args, kwargs

    def _process_result(self, func: F, result: Any) -> None:
        """
        *"Processes the result returned by a task."*

        A `protected` internal function that validates
        that every task in the sequence returns `None`.

        Args:
            func: The task function that produced the result.
            result: The result returned by the task function.

        Raises:
            InvalidReturnedValueError: If the task result is not `None`.
        """
        if result is not None:
            raise InvalidReturnedValueError(func, "None", 1)

    def _finalize_execution(self, *, exception: Exception | None = None) -> None:
        """
        *"Finalizes the execution of a task."*

        A `protected` internal function that updates the sequence status based on the
        outcome of the task execution. If an exception occurred,
        it handles the exception according to the sequence settings.

        Args:
            exception: The exception raised during task execution, if any.
        """
        self.__index += 1

        if exception is not None:
            self.__status.append(FAIL_STATUS)

            if not self._ignore_exceptions:
                raise exception

            return

        self.__status.append(OK_STATUS)

    def _abort_sequence(self) -> None:
        """
        *"Aborts the sequence execution due to an invalid return value."*

        A `protected` internal function that is called when a task returns an invalid value.
        It marks the current task as failed and fills the remaining tasks with a failed status.
        """
        for _ in range(self.remaining_steps):
            self.__status.append(FAIL_STATUS)
            self.__index += 1
        self.__loops += 1

    def walk(self, steps: int = 1) -> None:
        """
        *"Executes a specified number of steps in the sequence sync."*

        This method executes synchronously the tasks
        in the sequence for the given number of steps.
        If the end of the sequence is reached,
        a `StopIteration` exception is raised.

        Args:
            steps: The number of steps to execute. Defaults to 1.

        Raises:
            StopIteration: If the end of the sequence is reached before completing the specified steps.
        """
        for _ in range(steps):
            func, args, kwargs = self._prepare_execution()
            try:
                result: Any = func(*args, **kwargs)

                self._process_result(func, result)
            except InvalidReturnedValueError:
                self._abort_sequence()
                break
            except Exception as e:
                self._finalize_execution(exception=e)
            else:
                self._finalize_execution()

    async def walk_async(self, steps: int = 1) -> None:
        """
        *"Executes a specified number of steps in the sequence async."*

        This method executes asynchronously the tasks
        in the sequence for the given number of steps.
        If the end of the sequence is reached,
        a `StopIteration` exception is raised.

        Args:
            steps: The number of steps to execute. Defaults to 1.

        Raises:
            StopIteration: If the end of the sequence is reached before completing the specified steps.
        """
        for _ in range(steps):
            func, args, kwargs = self._prepare_execution()
            try:
                result: Any = func(*args, **kwargs)

                if inspect.isawaitable(result):
                    result = await result

                self._process_result(func, result)
            except InvalidReturnedValueError:
                self._abort_sequence()
                break
            except Exception as e:
                self._finalize_execution(exception=e)
            else:
                self._finalize_execution()

    def run(self) -> None:
        """
        *"Executes the entire sequence synchronously."*

        This method executes all tasks in the
        sequence synchronously until the end is reached.
        """
        while self.__index < self.total_steps:
            self.walk()
        self.__loops += 1
        
    async def run_async(self) -> None:
        """
        *"Executes the entire sequence asynchronously."*

        This method executes all tasks in the sequence
        asynchronously when needed until the end is reached.
        """
        while self.__index < self.total_steps:
            await self.walk_async()
        self.__loops += 1


    # ==================================================
    # Properties
    # ==================================================

    @property
    def ignore_exceptions(self) -> bool:
        """
        *"Returns if ignore exceptions is enabled."*

        Returns:
            bool: True if the sequence is set to ignore exceptions, False otherwise.
        """
        return self._ignore_exceptions
    
    @ignore_exceptions.setter
    def ignore_exceptions(self, value: bool) -> None:
        """
        *"Sets whether the sequence should ignore exceptions during execution."*

        Args:
            value: A boolean indicating whether to ignore exceptions (True) or not (False).
        """
        self._ignore_exceptions = value

    @property
    def loops(self) -> int:
        """
        *"Returns the number of loops completed by the sequence."*

        Returns:
            int: The number of loops completed.
        """
        return self.__loops
    
    @property
    def current_step(self) -> int:
        """
        *"Returns the current step number in the sequence."*

        Returns:
            int: The current step number.
        """
        return self.__index + 1
    
    @property
    def total_steps(self) -> int:
        """
        *"Returns the total number of steps in the sequence."*

        Returns:
            int: The total number of steps.
        """
        return len(self.tasks)
    
    @property
    def remaining_steps(self) -> int:
        """
        *"Returns the number of remaining steps in the sequence."*

        Returns:
            int: The number of remaining steps.
        """
        return len(self.tasks) - self.__index
