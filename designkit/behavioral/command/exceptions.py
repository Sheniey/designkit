
class InvokerException(Exception):
    pass

class NoCommandsToExecuteError(InvokerException):
    pass

class NoCommandsToUndoError(InvokerException):
    pass



class FunctionAsCommandException(Exception):
    pass

class UndoIsUndefinedError(FunctionAsCommandException):
    def __init__(self, func_name: str) -> None:
        super().__init__(f"Function {func_name} does not have an undo function defined")

class InvokerWarning(Warning):
    pass

class UndoesExceedHistoryWarning(InvokerWarning):
    def __init__(self, commands: int, history_length: int) -> None:
        super().__init__(f"Only {history_length} commands in history, undoing all of them instead of {commands}")

