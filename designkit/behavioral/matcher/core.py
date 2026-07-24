
import re
from typing import Final as Const, Callable, Any, Self
from collections.abc import Generator
from dataclasses import dataclass

from .exceptions import (
    MatchNotFoundError, NoMatchError, NoWasMatchedError,
    NoCasesMatchedError, UnsupportedTypeError, RecursionLimitExceededError
)


MAX_RECURSIONS: Const[int] = 10

type CaseFunction[R] = Callable[[Searcher], R]

@dataclass
class Case[T]:
    patterns: list[re.Pattern]
    func: CaseFunction[T]


class Capture:
    __slots__ = ('__value', '__capture_failure')

    def __init__(self, value: str, *, capture_failure: bool = False) -> None:
        self.__value: str = value
        self.__capture_failure: bool = capture_failure

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__value})'

    def __str__(self) -> str:
        return self.__value

    def __int__(self) -> int:
        return int(self.__value)
    
    def __float__(self) -> float:
        return float(self.__value)
    
    def __bool__(self) -> bool:
        return bool(self.__value)

    def as_string(self, *, default: str | None = None) -> str:
        return self.as_(str, default=default)

    def as_int(self, *, default: int | None = None) -> int:
        return self.as_(int, default=default)

    def as_float(self, *, default: float | None = None) -> float:
        return self.as_(float, default=default)

    def as_bool(self, *, default: bool | None = None) -> bool:
        return self.as_(bool, default=default)
    
    def as_[T](self, type: type[T], *, default: T | None = None) -> T:
        if self.__capture_failure:
            if default is not None:
                return default
            
            raise MatchNotFoundError(self.__value)
        return type(self.__value)

    @property
    def value(self) -> str:
        return self.__value

class Searcher:
    __slots__ = ('__value', '__match')

    def __init__(self, value: str, *, match: re.Match | None = None) -> None:
        self.__value: str = value
        self.__match: re.Match | None = match

    def __str__(self) -> str:
        return self.__value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.__value})'

    def __call__(self, pattern: str) -> Self:
        return self.search(pattern)
    
    def __getitem__(self, key: str) -> Capture:
        return self.load(key)

    def __getattr__(self, name: str) -> Any:
        if self.was_matched:
            return getattr(self.__match, name)
        raise NoWasMatchedError(self.__value)

    def search(self, pattern: str) -> Self:
        match: re.Match | None = re.search(pattern, self.__value)
        if match:
            self.__match: re.Match = match
            return self
        
        raise NoMatchError(pattern, self.__value)

    def load(self, catch: str) -> Capture:
        capture: Capture
        try:
            capture = Capture(
                value           = self.as_(lambda x: x, catch),
                capture_failure = False
            )

        except MatchNotFoundError:
            capture = Capture(
                value           = '',
                capture_failure = True
            )

        return capture

    def as_string(self, catch: str | None = None, *, default: str | None = None) -> str:
        return self.as_(str, catch, default=default)
    
    def as_int(self, catch: str | None = None, *, default: int | None = None) -> int:
        return self.as_(int, catch, default=default)
    
    def as_float(self, catch: str | None = None, *, default: float | None = None) -> float:
        return self.as_(float, catch, default=default)
    
    def as_bool(self, catch: str | None = None, *, default: bool | None = None) -> bool:
        return self.as_(bool, catch, default=default)
    
    def as_[T](self, type: type[T], catch: str | None = None, *, default: T | None = None) -> T:
        if self.was_matched:
            try:
                return type(self.__match.group(catch or 0))
            except IndexError:
                if default is not None:
                    return default
                
                raise MatchNotFoundError(self.__value, catch)
        
        raise NoWasMatchedError(self.__value)

    @property
    def was_matched(self) -> bool:
        return self.__match is not None

    @property
    def value(self) -> str:
        return self.__value

class Matcher[R]:
    __slots__ = ('__cases', '__recursion_depth')

    def __init__(self) -> None:
        self.__cases: list[Case[R]] = []
        self.__recursion_depth: int = 0

    def __add__(self, other: Matcher | list[Case] | Case) -> Self:
        if isinstance(other, Matcher):
            self.__cases.extend(other.cases)
        elif isinstance(other, list):
            self.__cases.extend(other)
        elif isinstance(other, Case):
            self.__cases.append(other)
        else:
            raise UnsupportedTypeError('__add__', type(other))
        
        return self

    def case(self, *patterns: str) -> Callable[[CaseFunction[R]], CaseFunction[R]]:
        def decorator(func: CaseFunction[R]) -> CaseFunction[R]:
            self.add_case(func, *patterns)
            return func
        return decorator

    def add_case(self, func: CaseFunction[R], *patterns: str) -> Self:
        compiled_patterns = [re.compile(pattern) for pattern in patterns]
        self.__cases.append(
            Case(
                patterns=compiled_patterns,
                func=func
            )
        )
        return self
    
    def _match_case(self, value: str) -> tuple[R, Searcher]:
        for case in self.__cases:
            patterns: list[re.Pattern] = case.patterns

            for pattern in patterns:
                if (m := pattern.fullmatch(value)):
                    self.__recursion_depth += 1
                    if self.__recursion_depth > MAX_RECURSIONS:
                        raise RecursionLimitExceededError(value, MAX_RECURSIONS)
                    
                    func: CaseFunction[R] = case.func
                    searcher: Searcher = Searcher(value, match=m)

                    try:
                        gen: R = func(searcher)
                        if not isinstance(gen, Generator):
                            return gen, searcher
                    finally:
                        self.__recursion_depth -= 1

                    # Example:
                    # ----------
                    # @...
                    # def a_by_fx(search: Searcher) -> Generator[str, None, str]:
                    #     a: int = search.as_int('a')
                    #     fx: str = search.as_string('fx')
                    #     fx_resolved, fx_search = yield fx
                    #     a *= fx_search.as_int(r'\d+')
                    #     return f'{a}{fx_resolved}'
                    #
                    # @...
                    # def pow_x_n(search: Searcher) -> str:
                    #     n: int = search.as_int('n')
                    #     x: str = search.as_string('x')
                    #     return f'{n}x^{n-1}'
                    #
                    # res = derive.match('5x^3')
                    #        \- a_by_fx --> {5}{?}       # yields
                    #            \- pow_x_n --> {3}x^{2} # returns
                    #        \- a_by_fx --> {15}x^{2}    # returns
                    #
                    # print(res) # Output: 15x^2
                    # ----------
                    last_result: R = None
                    last_searcher: Searcher = searcher
                    try:
                        expr: R = next(gen)
                    except StopIteration as e:
                        return e.value, searcher

                    while True:
                        last_result, last_searcher = self._match_case(expr)

                        try:
                            expr: R = gen.send((last_result, last_searcher))
                        except StopIteration as e:
                            return e.value, searcher

        raise NoCasesMatchedError(value)

    def match(self, value: str) -> R:
        result, _ = self._match_case(value)
        return result

    @property
    def cases(self) -> list[Case[R]]:
        return self.__cases
