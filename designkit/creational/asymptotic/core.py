
from designkit.creational.asymptotic.models import Expression, Fx


def _Asymptotic(name: str, attribute: str, c_temp: Expression | None = None, c_space: Expression | None = None):
    if c_temp is None and c_space is None:
        raise ValueError('At least one of temporal or space complexity expressions must be provided.')

    def decorator(func):
        setattr(func, attribute, (c_temp, c_space))
        return func

    return decorator

def BigO(*, c_temp: Expression | None = None, c_space: Expression | None = None):
    """`O(...)` : Upper bound on the growth rate of the function."""
    return _Asymptotic('O', '__asymptotic_bigo__', c_temp, c_space)

def BigOmega(*, c_temp: Expression | None = None, c_space: Expression | None = None):
    """`Ω(...)` : Lower bound on the growth rate of the function."""
    return _Asymptotic('Ω', '__asymptotic_bigomega__', c_temp, c_space)

def BigTheta(*, c_temp: Expression | None = None, c_space: Expression | None = None):
    """`Θ(...)` : Tight bound on the growth rate of the function."""
    return _Asymptotic('Θ', '__asymptotic_bigtheta__', c_temp, c_space)

def LilO(*, c_temp: Expression | None = None, c_space: Expression | None = None):
    """`o(...)` : Strict upper bound on the growth rate of the function."""
    return _Asymptotic('o', '__asymptotic_lilo__', c_temp, c_space)
 
def LilOmega(*, c_temp: Expression | None = None, c_space: Expression | None = None):
    """`ω(...)` : Strict lower bound on the growth rate of the function."""

    return _Asymptotic('ω', '__asymptotic_lilomega__', c_temp, c_space)
def LilTheta(*, c_temp: Expression | None = None, c_space: Expression | None = None):
    """`θ(...)` : Strict tight bound on the growth rate of the function."""
    return _Asymptotic('θ', '__asymptotic_liltheta__', c_temp, c_space)

