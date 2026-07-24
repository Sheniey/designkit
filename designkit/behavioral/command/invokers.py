
from collections import deque
from typing import Any
import inspect, multiprocessing as mp

from .exceptions import (
    UndoesExceedHistoryWarning
)
from .models import ProcessMetadata
from .commands import (
    _Command,
    Command, AsyncCommand, ProcessCommand
)

class _Invoker[C: _Command]:
    def __init__(self, max_history: int = 100) -> None:
        self.__pipeline: deque[C] = deque()

        self.__history: deque[tuple[C, ProcessMetadata]] = deque()
        self.__max_history: int = max_history

        self.__allowed_commands: set[type[C]] = set()
        self.__all_commands_allowed: bool = False

    def __add__(self, command: C) -> Invoker[C]:
        self.push_command(command)
        return self

    def __sub__(self, command: C) -> Invoker[C]:
        self.__pipeline.remove(command)
        return self
    
    def __len__(self) -> int:
        return len(self.__pipeline)

    def allow_all_commands(self) -> None:
        self.__all_commands_allowed = True

    def allow_command(self, command: type[C]) -> None:
        self.__allowed_commands.add(command)

    def disallow_command(self, command: type[C]) -> None:
        self.__allowed_commands.discard(command)

    def push_command(self, command: C) -> None:
        self.__pipeline.append(command)

    def pop_command(self) -> C:
        return self.__pipeline.pop()

    def go_back(self, commands: int = 5) -> None:
        if commands > len(self.__history):
            raise UndoesExceedHistoryWarning(commands, len(self.__history))

        for _ in range(min(commands, len(self.__history))):
            self.undo()

    @property
    def pipeline(self) -> list[C]:
        return list(self.__pipeline)
    
    @pipeline.setter
    def pipeline(self, commands: list[C]) -> None:
        self.__pipeline = deque(commands)

    @pipeline.deleter
    def pipeline(self) -> None:
        self.__pipeline.clear()

    @property
    def history(self) -> list[tuple[C, ProcessMetadata]]:
        return list(self.__history)

    @history.deleter
    def history(self) -> None:
        self.__history.clear()

    @property
    def whitelist(self) -> set[type[C]]:
        return self.__allowed_commands
    
    @whitelist.setter
    def whitelist(self, commands: set[type[C]]) -> None:
        self.__allowed_commands = commands

    @whitelist.deleter
    def whitelist(self) -> None:
        self.__allowed_commands.clear()


class Invoker[C: Command](_Invoker):
    def execute(self) -> None:
        workflow: list[C] = [
            command
            for command in self.__pipeline
            if self.__all_commands_allowed
            or type(command) in self.__allowed_commands
        ]
        for command in workflow:
            self.__pipeline.remove(command)
            command()
            self.__history.append((command, ProcessMetadata()))
            if len(self.__history) > self.__max_history:
                self.__history.pop(0)

    def undo(self) -> None:
        if not self.__history:
            return
        last_command, _ = self.__history.pop()
        last_command.undo()

class AsyncInvoker[C: AsyncCommand](_Invoker):
    async def execute(self) -> None:
        workflow: list[C] = [
            command
            for command in self.__pipeline
            if self.__all_commands_allowed
            or type(command) in self.__allowed_commands
        ]
        for command in workflow:
            self.__pipeline.remove(command)
            result: Any = command()
            if inspect.isawaitable(result):
                await result
            else:
                result
            self.__history.append((command, ProcessMetadata()))
            if len(self.__history) > self.__max_history:
                self.__history.pop(0)

    async def undo(self) -> None:
        if not self.__history:
            return
        last_command, _ = self.__history.pop()
        await last_command.undo()

class ProcessInvoker[C: ProcessCommand](_Invoker):
    def __init__(self, max_history: int = 100) -> None:
        super().__init__(max_history)
        self.__pool = mp.Pool(processes=mp.cpu_count())

    def execute(self) -> None:
        workflow: list[C] = [
            command
            for command in self.__pipeline
            if self.__all_commands_allowed
            or type(command) in self.__allowed_commands
        ]
        with self.__pool as pool:
            for command in workflow:
                self.__pipeline.remove(command)
                result: ProcessMetadata = pool.apply(command.execute)
                self.__history.append((command, result))
                if len(self.__history) > self.__max_history:
                    self.__history.pop(0)
    
    def undo(self) -> None:
        if not self.__history:
            return
        last_command, metadata = self.__history.pop()
        with self.__pool as pool:
            pool.apply(last_command.undo, args=(metadata,))
        
    def block(self) -> None:
        self.__pool.close()
        self.__pool.join()
