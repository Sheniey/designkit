
from typing import Generic
from abc import ABC, abstractmethod
from typing import Callable


class Expression[I](ABC):
    @abstractmethod
    def interpret(self) -> I:
        pass



class ExpressionUnit[I](Expression[I]):
    def __init__(self, value: I, /) -> None:
        if not self.condition(value):
            raise ValueError(f'Invalid value for {self.__class__.__name__}: {value}')

        self.value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value})'

    def condition(self, value: I) -> bool:
        return True

    def interpret(self) -> I:
        return self.value



class SingleArgumentExpression[A: Expression, I](Expression[I]):
    symbol: str = '?'
    
    def __init__(self, target: A, /) -> None:
        self.target: A = target

    def __repr__(self) -> str:
        return f'[{self.symbol}] {self.__class__.__name__}\n{self.target!r}'

    @abstractmethod
    def interpret(self) -> I:
        pass

class DoubleArgumentExpression[L: Expression, R: Expression, I](Expression[I]):
    symbol: str = '?'

    def __init__(self, left: L, right: R, /) -> None:
        self.left: L = left
        self.right: R = right

    def __repr__(self) -> str:
        return f'[{self.symbol}] {self.__class__.__name__}\n{self.left!r}\n{self.right!r}'

    def type_policy(self, ltype: type, rtype: type) -> tuple[L, R]:
        if not isinstance(self.left.interpret(), ltype):
            raise TypeError(f'Left expression must evaluate to {ltype.__name__}.')
        if not isinstance(self.right.interpret(), rtype):
            raise TypeError(f'Right expression must evaluate to {rtype.__name__}.')
        return self.left, self.right
    
    @abstractmethod
    def interpret(self) -> I:
        pass

class TernaryArgumentExpression[A: Expression, B: Expression, C: Expression, I](Expression[I]):
    symbol: str = '?'

    def __init__(self, first: A, second: B, third: C, /) -> None:
        self.first: A = first
        self.second: B = second
        self.third: C = third

    def __repr__(self) -> str:
        return f'[{self.symbol}] {self.__class__.__name__}\n{self.first!r}\n{self.second!r}\n{self.third!r}'

    @abstractmethod
    def interpret(self) -> I:
        pass

class QuaternaryArgumentExpression[A: Expression, B: Expression, C: Expression, D: Expression, I](Expression[I]):
    symbol: str = '?'
    
    def __init__(self, first: A, second: B, third: C, fourth: D, /) -> None:
        self.first: A = first
        self.second: B = second
        self.third: C = third
        self.fourth: D = fourth

    def __repr__(self) -> str:
        return f'[{self.symbol}] {self.__class__.__name__}\n{self.first!r}\n{self.second!r}\n{self.third!r}\n{self.fourth!r}'

    @abstractmethod
    def interpret(self) -> I:
        pass
