
class MemorableError(Exception):
    """Base class for exceptions in this module."""
    pass



class EmptyMemoryError(MemorableError):
    """Raised when trying to pop an item from an empty stack, queue, deque, or heap."""

    iterator: str = "Iterator"

    def __init__(self) -> None:
        super().__init__(
            f"The '{self.iterator}' is empty! "
            f"Push some items before trying to pop."
        )

class StackEmptyError(EmptyMemoryError): iterator: str = "Stack"
class QueueEmptyError(EmptyMemoryError): iterator: str = "Queue"
class DequeEmptyError(EmptyMemoryError): iterator: str = "Deque"
class HeapEmptyError(EmptyMemoryError): iterator: str = "Heap"



class FullCapacityError(MemorableError):
    """Raised when trying to push an item into a full stack, queue, deque, or heap."""

    iterator: str = "Iterator"

    def __init__(self) -> None:
        super().__init__(
            f"The '{self.iterator}' is at full capacity! "
            f"Extend the max capacity or remove some items."
        )

class StackFullError(FullCapacityError): iterator: str = "Stack"
class QueueFullError(FullCapacityError): iterator: str = "Queue"
class DequeFullError(FullCapacityError): iterator: str = "Deque"
class HeapFullError(FullCapacityError): iterator: str = "Heap"
