
from dataclasses import dataclass
from enum import Enum, IntEnum


class Status(IntEnum):
    VERY_FINE = 1
    FINE = 2
    WARNING = 3
    HIGH = 4
    CRITICAL = 5

class BinaryOperator(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    POW = '^'

class UnaryOperator(Enum):
    NEG = '-'



@dataclass(frozen=True, slots=True)
class Constant:
    value: int | float

@dataclass(frozen=True, slots=True)
class Variable:
    name: str

@dataclass(frozen=True, slots=True)
class Binary:
    left: Node
    operator: BinaryOperator
    right: Node

@dataclass(frozen=True, slots=True)
class Unary:
    operator: UnaryOperator
    operand: Node

@dataclass(frozen=True, slots=True)
class Function:
    name: str
    arguments: tuple[Node, ...]


type Node = (
      Constant
    | Variable
    | Binary
    | Unary
    | Function
)



class Expression:
    """
    Mathematical expression backed by an AST.

    Examples
    --------
    `Fx.n`
    
    `Fx.n + 1`
    
    `Fx.n ** 2`
    
    `(Fx.n + 1) ** 2`
    
    `Fx.log(Fx.n)`
    """

    __slots__ = ('__node', '__status')

    def __init__(
        self,
        node: Node,
        status: Status = Status.VERY_FINE,
    ) -> None:
        self.__node = node
        self.__status = status

    def __str__(self) -> str:
        return _format(self.node)

    def __repr__(self) -> str:
        return (
            f'Expression('
            f'node={self.node!r}, '
            f'status={self.status.name})'
        )

    def __add__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                self.node,
                BinaryOperator.ADD,
                other.node,
            ),
            self._combine_status(other),
        )

    def __radd__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        return self.__add__(other)

    def __sub__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                self.node,
                BinaryOperator.SUB,
                other.node,
            ),
            self._combine_status(other),
        )

    def __rsub__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                other.node,
                BinaryOperator.SUB,
                self.node,
            ),
            self._combine_status(other),
        )

    def __mul__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                self.node,
                BinaryOperator.MUL,
                other.node,
            ),
            self._combine_status(other),
        )

    def __rmul__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        return self.__mul__(other)

    def __truediv__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                self.node,
                BinaryOperator.DIV,
                other.node,
            ),
            self._combine_status(other),
        )

    def __rtruediv__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                other.node,
                BinaryOperator.DIV,
                self.node,
            ),
            self._combine_status(other),
        )

    def __pow__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                self.node,
                BinaryOperator.POW,
                other.node,
            ),
            self._combine_status(other),
        )

    def __rpow__(
        self,
        other: int | float | Expression,
    ) -> Expression:
        other = self._coerce(other)

        if other is NotImplemented:
            return NotImplemented

        return Expression(
            Binary(
                other.node,
                BinaryOperator.POW,
                self.node,
            ),
            self._combine_status(other),
        )

    def __neg__(self) -> Expression:
        return Expression(
            Unary(
                UnaryOperator.NEG,
                self.node,
            ),
            self.status,
        )


    @classmethod
    def constant(cls, value: int | float, status: Status = Status.VERY_FINE) -> Expression:
        return cls(Constant(value), status)

    @classmethod
    def variable(cls, name: str, status: Status = Status.VERY_FINE) -> Expression:
        return cls(Variable(name), status)

    @classmethod
    def function(cls, name: str, *arguments: Expression, status: Status = Status.VERY_FINE) -> Expression:
        return cls(
            Function(name, tuple(argument.node for argument in arguments)),
            status
        )

    @staticmethod
    def _coerce(value: int | float | Expression) -> Expression:
        if isinstance(value, Expression):
            return value
        if isinstance(value, (int, float)):
            return Expression.constant(value)
        return NotImplemented

    def _combine_status(self, other: int | float | Expression,) -> Status:
        if isinstance(other, Expression):
            return max(self.status, other.status)
        return self.status

 
    def log(self) -> Expression:
        return Expression(
            Function(
                'log',
                (self.node,),
            ),
            self.status,
        )

    @property
    def node(self) -> Node:
        return self.__node

    @property
    def status(self) -> Status:
        return self.__status



_PRECEDENCE: dict[BinaryOperator, int] = {
    BinaryOperator.ADD: 10,
    BinaryOperator.SUB: 10,
    BinaryOperator.MUL: 20,
    BinaryOperator.DIV: 20,
    BinaryOperator.POW: 30,
}


def _format(node: Node, parent_precedence: int = 0) -> str:
    match node:
        case Constant(value=value):
            return str(value) 
        case Variable(name=name):
            return name
        case Function(name=name, arguments=arguments):
            formatted_arguments = ', '.join(_format(argument) for argument in arguments)
            return f'{name}({formatted_arguments})' 
        case Unary(operator=operator, operand=operand):
            expression = _format(operand, 40)
            result = f'{operator.value}{expression}'
            if 40 < parent_precedence:
                return f'({result})'
            return result
        case Binary(operator=operator, left=left, right=right):
            precedence = _PRECEDENCE[operator]
            left_formatted = _format(left, precedence)
            right_formatted = _format(right, precedence)
            if operator is BinaryOperator.POW: # in case of exponentiation, no spaces around the operator
                result = f'{left_formatted}{operator.value}{right_formatted}'
            else:
                result = f'{left_formatted} {operator.value} {right_formatted}'
            
            if precedence < parent_precedence:
                return f'({result})'
            return result
        case _:
            raise TypeError(f'Unknown AST node: {type(node)!r}')


class Fx:
    n = Expression.variable('n')
    m = Expression.variable('m')

    @staticmethod
    def log(n: int | float | Expression) -> Expression:
        n: Expression = Expression._coerce(n)
        if n is NotImplemented:
            raise TypeError(f'Unsupported type for log(): {type(n)!r}')

        return Expression(
            Function('log', (n.node,)),
            n.status
        )

    @staticmethod
    def min(*values: int | float | Expression) -> Expression:
        expressions: tuple[Expression, ...] = tuple(
            Expression._coerce(value)
            for value in values
        )

        if any(value is NotImplemented for value in expressions):
            raise TypeError('Fx.min() only accepts int, float or Expression.')

        status: Status = max(
            (value.status for value in expressions),
            default=Status.VERY_FINE
        )

        return Expression(
            Function('min', tuple(value.node for value in expressions)),
            status,
        )

    @staticmethod
    def max(*values: int | float | Expression) -> Expression:
        expressions: tuple[Expression, ...] = tuple(
            Expression._coerce(value)
            for value in values
        )

        if any(value is NotImplemented for value in expressions):
            raise TypeError(
                'Fx.max() only accepts int, float or Expression.'
            )

        status: Status = max(
            (value.status for value in expressions),
            default=Status.VERY_FINE,
        )

        return Expression(
            Function('max', tuple(value.node for value in expressions)),
            status,
        )

