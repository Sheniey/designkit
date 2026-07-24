
from .iter_types import IteratorBase


class IteratorException(Exception):
    pass

NO_MORE_ITEMS_ERROR = "The iterator has no more items to iterate over."



class IterationNotStartedError(IteratorException):
    def __init__(self, iterator: IteratorBase) -> None:
        super().__init__(
            f"The iterator {iterator.__class__.__name__} has not been started yet."
            f"Advance the iterator before accessing the current item."
        )

class UnsupportedOperationError(NotImplementedError, IteratorException):
    def __init__(self, operation: str) -> None:
        super().__init__(f"Operation {operation} is not supported by this iterator.")

class InvalidIteratorStateError(IteratorException):
    def __init__(self, operation: str, required: str) -> None:
        super().__init__(f"Cannot do '{operation}' without first doing '{required}'.")

class IndexOutOfBoundsError(IndexError, IteratorException):
    def __init__(self, operation: str, index: int, coll_length: int) -> None:
        super().__init__(
            f"Operation '{operation}' cannot access index [{index}]; "
            f"collection size is {coll_length}."
        )
class SavepointIdMismatchError(IteratorException):
    def __init__(self, savepoint_id: int, iterator: IteratorBase) -> None:
        super().__init__(f"Savepoint ID mismatch: the id [{savepoint_id}] does not match the iterator {iterator.__class__.__name__}.")
