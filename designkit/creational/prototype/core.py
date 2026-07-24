
from typing import Self
import copy

class Cloneable:
    def clone(self, deep: bool = False) -> Self:
        """
        *"It self-copies w/everything."*

        Creates a copy of the object. If deep is True, it creates a deep copy; otherwise, it creates a shallow copy.
        
        Example:
            >>> class MyClass(Cloneable):
            ...    def __init__(self, value) -> None:
            ...        self.value = value
            >>>
            >>> obj1: MyClass = MyClass(10)
            >>> obj2: MyClass = obj1.clone()          # Shallow copy
            >>> obj3: MyClass = obj1.clone(deep=True) # Deep copy

        Args:
            deep (bool): If True, creates a deep copy of the object. Defaults to False (shallow copy).

        Returns:
            Self: A copy of the object.
        """

        if deep:
            return copy.deepcopy(self)
        return copy.copy(self)
