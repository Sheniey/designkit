
import math
from .core import (
    SingleArgumentExpression as SAE,
    DoubleArgumentExpression as DAE,
    Expression as Expr
)


# ==================================================
# ¬x / !x / -x / not x
# ==================================================

class Negate[A: Expr, I](SAE[A, I]):
    symbol: str = '¬'

    def interpret(self) -> I:
        return -self.target.interpret()



# ==================================================
# |x| / abs(x)  |  [x]
# ==================================================

class Absolute[A: Expr, I](SAE[A, I]):
    symbol: str = '|x|'
    def interpret(self) -> I:
        return abs(self.target.interpret())

class Floor[A: Expr, I](SAE[A, I]):
    def interpret(self) -> I:
        return math.floor(self.target.interpret())



# ==================================================
# x + y  |  x - y
# ==================================================

class Add[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '+'

    def interpret(self) -> I:
        return self.left.interpret() + self.right.interpret()

class Subtract[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '-'

    def interpret(self) -> I:
        return self.left.interpret() - self.right.interpret()



# ==================================================
# x * y  |  x / y
# ==================================================

class Multiply[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '*'

    def interpret(self) -> I:
        return self.left.interpret() * self.right.interpret()
    
class Divide[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '/'

    def interpret(self) -> I:
        return self.left.interpret() / self.right.interpret()



# ==================================================
# x^y  |  x²  |  √x  |  2√x
# ==================================================

class Power[A: Expr, B: Expr, I](DAE[A, B, I]):
    symbol: str = '^'

    def interpret(self) -> I:
        return self.left.interpret() ** self.right.interpret()
    
class Squared[A: Expr, I](SAE[A, I]):
    symbol: str = '²'

    def interpret(self) -> I:
        return self.target.interpret() ** 2

class Root[A: Expr, B: Expr, I](DAE[A, B, I]):
    symbol: str = '√'

    def interpret(self) -> I:
        return math.pow(self.left.interpret(), 1 / self.right.interpret())

class SQRT[A: Expr, I](SAE[A, I]):
    symbol: str = '√'

    def interpret(self) -> I:
        return self.target.interpret() ** 0.5



# ==================================================
# x!  |  x%  |  x mod y
# ==================================================

class Factorial[A: Expr, I](SAE[A, I]):
    symbol: str = '!'

    def interpret(self) -> I:
        return math.factorial(self.target.interpret())
    
class Percent[A: Expr, I](SAE[A, I]):
    symbol: str = '%'

    def interpret(self) -> I:
        return self.target.interpret() / 100
    
class Modulo[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = 'mod'

    def interpret(self) -> I:
        return self.left.interpret() % self.right.interpret()



# ==================================================
# x == y  |  x != y  |  x ~= y  |  x !~= y
# ==================================================

class Equal[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '=='
    
    def interpret(self) -> I:
        return self.left.interpret() == self.right.interpret()
    
class NotEqual[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '!='

    def interpret(self) -> I:
        return self.left.interpret() != self.right.interpret()
    
class ApproxEqual[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '~='
    
    def interpret(self) -> I:
        return math.isclose(self.left.interpret(), self.right.interpret())

class NotApproxEqual[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '!~='
    
    def interpret(self) -> I:
        return not math.isclose(self.left.interpret(), self.right.interpret())



# ==================================================
# x is y  |  x is not y
# ==================================================

class ExactlyEqual[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = 'is'
    
    def interpret(self) -> I:
        return self.left.interpret() is self.right.interpret()

class NotExactlyEqual[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = 'is not'
    
    def interpret(self) -> I:
        return self.left.interpret() is not self.right.interpret()

type Is[L: Expr, R: Expr, I] = ExactlyEqual[L, R, I]
type IsNot[L: Expr, R: Expr, I] = NotExactlyEqual[L, R, I]



# ==================================================
# x < y  |  x > y  |  x <= y  |  x >= y 
# ==================================================

class LessThan[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '<'
    
    def interpret(self) -> I:
        return self.left.interpret() < self.right.interpret()
    
class GreaterThan[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '>'

    def interpret(self) -> I:
        return self.left.interpret() > self.right.interpret()
    
class LessThanOrEqual[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '<='

    def interpret(self) -> I:
        return self.left.interpret() <= self.right.interpret()
    
class GreaterThanOrEqual[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = '>='

    def interpret(self) -> I:
        return self.left.interpret() >= self.right.interpret()



# ==================================================
# x in Y  |  x not in Y
# ==================================================

class BelongsTo[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = 'in'

    def interpret(self) -> I:
        return self.left.interpret() in self.right.interpret()

class NotBelongsTo[L: Expr, R: Expr, I](DAE[L, R, I]):
    symbol: str = 'not in'

    def interpret(self) -> I:
        return self.left.interpret() not in self.right.interpret()

type In[L: Expr, R: Expr, I] = BelongsTo[L, R, I]
type NotIn[L: Expr, R: Expr, I] = NotBelongsTo[L, R, I]



# ==================================================
# Ax  |  Ex  |  !Ex
# ==================================================

class UniversalSet[A: Expr, I](SAE[A, I]):
    symbol: str = 'A'
    
    def interpret(self) -> I:
        return all(self.target.interpret())

class Exists[A: Expr, I](SAE[A, I]):
    symbol: str = 'E'

    def interpret(self) -> I:
        return any(self.target.interpret())
    
class NotExists[A: Expr, I](SAE[A, I]):
    symbol: str = '!E'
    
    def interpret(self) -> I:
        return not any(self.target.interpret())

type ForAll[A: Expr, I] = UniversalSet[A, I]
type All[A: Expr, I] = UniversalSet[A, I]
type Any[A: Expr, I] = Exists[A, I]
