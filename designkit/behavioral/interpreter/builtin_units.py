
from typing import Never
from .core import Expression as Expr, ExpressionUnit


# ==================================================
# None
# ==================================================

class NoneType[I](Expr):
    def __init__(self, value: I | Never = Never, /) -> None:
        self.value: I | None = None

    def condition(self, value: None) -> bool:
        return True
    
    def interpret(self) -> None:
        return self.value

type Null = NoneType[None]
type Void = NoneType[None]
type Undefined = NoneType[None]
type Nil = NoneType[None]
type Nothing = NoneType[None]



# ==================================================
# Numeric
# ==================================================

class Digit(ExpressionUnit[int]):
    def condition(self, value: int) -> bool:
        return isinstance(value, int) and 0 <= value <= 9

class Number(ExpressionUnit[float]):
    def condition(self, value: float) -> bool:
        return isinstance(value, (int, float))

class Natural(ExpressionUnit[int]):
    def condition(self, value: int) -> bool:
        return isinstance(value, int) and value >= 0

class Integer(ExpressionUnit[int]):
    def condition(self, value: int) -> bool:
        return isinstance(value, int)
    
class Float(ExpressionUnit[float]):
    def condition(self, value: float) -> bool:
        return isinstance(value, float)
    
type Real = Float



# ==================================================
# Text
# ==================================================

class Char(ExpressionUnit[str]):
    def condition(self, value: str) -> bool:
        return isinstance(value, str) and len(value) == 1

class String(ExpressionUnit[str]):
    def condition(self, value: str) -> bool:
        return isinstance(value, str)

type Text = String



# ==================================================
# Boolean
# ==================================================

class Boolean(ExpressionUnit[bool]):
    def condition(self, value: bool) -> bool:
        return isinstance(value, bool)
    
class Bytes(ExpressionUnit[bytes]):
    def condition(self, value: bytes) -> bool:
        return isinstance(value, bytes)



# ==================================================
# Iterator
# ==================================================

class Iterator[A: Expr](ExpressionUnit[iter]):
    def condition(self, value: iter[A]) -> bool:
        return isinstance(value, iter) and all(isinstance(item, A) for item in value)

class List[A: Expr](ExpressionUnit[list[A]]):
    def condition(self, value: list[A]) -> bool:
        return isinstance(value, list) and all(isinstance(item, A) for item in value)

class Tuple[A: Expr](ExpressionUnit[tuple[A]]):
    def condition(self, value: tuple[A]) -> bool:
        return isinstance(value, tuple) and all(isinstance(item, A) for item in value)
    
class Set[A: Expr](ExpressionUnit[set[A]]):
    def condition(self, value: set[A]) -> bool:
        return isinstance(value, set) and all(isinstance(item, A) for item in value)
    
class Dict[K: Expr, V: Expr](ExpressionUnit[dict[K, V]]):
    def condition(self, value: dict[K, V]) -> bool:
        return isinstance(value, dict) and all(isinstance(k, K) and isinstance(v, V) for k, v in value.items())
    
type Array[A: Expr] = List[A]
type Map[K: Expr, V: Expr] = Dict[K, V]
type HashMap[K: Expr, V: Expr] = Dict[K, V]
