
import inspect, time, asyncio
from typing import Self, Callable, Literal


type Target = object | Callable | type


class Assertion:
    """
    A class for asserting conditions on objects.
    """
    __slots__ = ('__target', '__target_kind', '__async_fn', '__args_fn', '__kwargs_fn')

    _assertion_cache: dict[str, bool] = {}
    _assertion_cache_max_size: int = 24


    def __init__(self, target: Target, *args, **kwargs) -> None:
        """
        Initialize an Assertion instance with a target object, function, or class.

        Args:
            target (Target): The object, function, or class to assert conditions on.
            *args: Positional arguments for the target if it is callable.
            **kwargs: Keyword arguments for the target if it is callable.
        """
        self.__target: Target = target
        self.__target_kind: Literal['class', 'function', 'object'] = 'class' if inspect.isclass(target) else 'function' if callable(target) else 'object'

        self.__async_fn: bool = inspect.iscoroutinefunction(target) or inspect.isasyncgenfunction(target)
        self.__args_fn: tuple = args
        self.__kwargs_fn: dict[str, object] = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}( {self.__target!r} )'

    def __str__(self) -> str:
        return repr(self)

    def __getcache__(self, feature: str) -> tuple[bool, bool]:
        value: bool | None = Assertion._assertion_cache.get(f'{feature}:{id(self.__target)}', None)
        is_cached: bool = value is not None
        return value or False, is_cached

    def __setcache__(self, feature: str, value: bool) -> None:
        key: str = f'{feature}:{id(self.__target)}'
        if key not in Assertion._assertion_cache and len(Assertion._assertion_cache) >= Assertion._assertion_cache_max_size:
            oldest_key = next(iter(Assertion._assertion_cache))
            del Assertion._assertion_cache[oldest_key]
        Assertion._assertion_cache[key] = value

    def __delcache__(self, feature: str) -> None:
        key: str = f'{feature}:{id(self.__target)}'
        if key in Assertion._assertion_cache:
            del Assertion._assertion_cache[key]


    _CACHE_COMPLY = 'comply'
    def _comply(self, condition: Callable[[Target], bool]) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_COMPLY)
        if is_cached: return cached

        comply: bool = condition(self.__target)
        self.__setcache__(Assertion._CACHE_COMPLY, comply)
        return comply

    def assert_comply(self, message: str, condition: Callable[[Target], bool]) -> Self:
        """Assert that an object complies with a given condition."""
        if not self._comply(condition):
            self.__delcache__(Assertion._CACHE_COMPLY)
            raise AssertionError(message)
        return self
    
    def must_comply(self, condition: Callable[[Target], bool], custom_expt: type[Exception] = AssertionError) -> None:
        """Require that an object complies with a given condition."""
        if not self._comply(condition):
            self.__delcache__(Assertion._CACHE_COMPLY)
            raise custom_expt(f'Object {self.__target} does not comply with the given condition')

    def should_comply(self, condition: Callable[[Target], bool]) -> bool:
        """Check that an object complies with a given condition."""
        return condition(self.__target)


    _CACHE_BE_VOID = 'be_void'
    def _be_void(self) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_BE_VOID)
        if is_cached: return cached

        is_void: bool = self.__target is not None or not self.__target
        self.__setcache__(Assertion._CACHE_BE_VOID, is_void)
        return is_void

    def assert_be_void(self, message: str) -> Self:
        """Assert that an object is not None or empty."""
        if not self._be_void():
            self.__delcache__(Assertion._CACHE_BE_VOID)
            raise AssertionError(message)
        return self

    def must_be_void(self, custom_expt: type[Exception] = ValueError) -> None:
        """Require that an object is not None or empty."""
        if not self._be_void():
            self.__delcache__(Assertion._CACHE_BE_VOID)
            raise custom_expt(f'Object {self.__target} is None or empty')

    def should_be_void(self) -> bool:
        """Check that an object is not None or empty."""
        return self._be_void()


    _CACHE_BE = 'be_type'
    def _be(self, *types: type) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_BE)
        if is_cached: return cached

        fil_types: list = list(filter(lambda t: t is not None, types))
        if len(fil_types) < len(types) and self.__target is None:
            self.__setcache__(Assertion._CACHE_BE, True)
            return True
        
        if (
            # literal type check
            any(isinstance(self.__target, t) for t in fil_types)
            or
            # duck type check
            any(issubclass(type(self.__target), t) for t in fil_types)
            or
            # attribute check -- weird ik
            getattr(self.__target, '__dict__', None) and not any(hasattr(self.__target, attr) for attr in dir(self.__target) if not attr.startswith('__'))
        ):
            self.__setcache__(Assertion._CACHE_BE, True)
            return True
        self.__setcache__(Assertion._CACHE_BE, False)
        return False

    def assert_be(self, message: str, *types: type) -> Self:
        """Assert that an object is of a certain type."""
        if not self._be(*types):
            self.__delcache__(Assertion._CACHE_BE)
            raise AssertionError(message)
        return self

    def must_be(self, *types: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is of a certain type."""
        if not self._be(*types):
            self.__delcache__(Assertion._CACHE_BE)
            raise custom_expt(f'Object {self.__target} is not one of the following types {", ".join(classname(t) for t in types)}')

    def should_be(self, *types: type) -> bool:
        """Check that an object is of a certain type."""
        return self._be(*types)


    _CACHE_HAVE = 'have'
    def _have(self, *attributes: str) -> tuple[bool, list[str]]:
        cached, is_cached = self.__getcache__(Assertion._CACHE_HAVE)
        if is_cached: return cached, []
        
        missing = [attr for attr in attributes if not hasattr(self.__target, attr)]
        self.__setcache__(Assertion._CACHE_HAVE, not missing)
        return not missing, missing

    def assert_have(self, message: str, *attributes: str) -> Self:
        """Assert that an object has certain attributes."""
        has_all, missing = self._have(*attributes)
        if not has_all:
            self.__delcache__(Assertion._CACHE_HAVE)
            raise AssertionError(message)
        return self

    def must_have(self, *attributes: str, custom_expt: type[Exception] = AttributeError) -> None:
        """Require that an object has certain attributes."""
        has_all, missing = self._have(*attributes)
        if not has_all:
            self.__delcache__(Assertion._CACHE_HAVE)
            raise custom_expt(f'Object {self.__target} does not have attributes {missing}')

    def should_have(self, *attributes: str) -> bool:
        """Check that an object has certain attributes."""
        has_all, _ = self._have(*attributes)
        return has_all


    _CACHE_IMPLEMENT = 'implements'
    def _implement(self, *methods: str | Callable) -> tuple[bool, list[str]]:
        cached, is_cached = self.__getcache__(Assertion._CACHE_IMPLEMENT)
        if is_cached: return cached, []

        get_name = lambda method: method.__name__ if callable(method) else method
        missing = [
            get_name(method)
            for method in methods
            if not callable(getattr(self.__target, get_name(method), None))
        ]
        self.__setcache__(Assertion._CACHE_IMPLEMENT, not missing)
        return not missing, missing

    def assert_implement(self, message: str, *methods: str | Callable) -> Self:
        """Assert that an object implements certain methods."""
        has_all, missing = self._implement(*methods)
        if not has_all:
            self.__delcache__(Assertion._CACHE_IMPLEMENT)
            raise AssertionError(message)
        return self

    def must_implement(self, *methods: str | Callable, custom_expt: type[Exception] = NotImplementedError) -> None:
        """Require that an object implements certain methods."""
        has_all, missing = self._implement(*methods)
        if not has_all:
            self.__delcache__(Assertion._CACHE_IMPLEMENT)
            raise custom_expt(f'Object {self.__target} does not implement methods {missing}')

    def should_implement(self, *methods: str | Callable) -> bool:
        """Check that an object implements certain methods."""
        has_all, _ = self._implement(*methods)
        return has_all


    _CACHE_INHERIT = 'inherits'
    def _inherit(self, *base_classes: type) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_INHERIT)
        if is_cached: return cached

        cls = self.__target if inspect.isclass(self.__target) else type(self.__target)
        inherits: bool = any(issubclass(cls, base) for base in base_classes)
        self.__setcache__(Assertion._CACHE_INHERIT, inherits)
        return inherits

    def assert_inherit(self, message: str, *base_classes: type) -> Self:
        """Assert that an object inherits from certain base classes."""
        if not self._inherit(*base_classes):
            self.__delcache__(Assertion._CACHE_INHERIT)
            raise AssertionError(message)
        return self

    def must_inherit(self, *base_classes: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object inherits from certain base classes."""
        if not self._inherit(*base_classes):
            self.__delcache__(Assertion._CACHE_INHERIT)
            raise custom_expt(f'Object {self.__target} does not inherit from {base_classes}')

    def should_inherit(self, *base_classes: type) -> bool:
        """Check that an object inherits from certain base classes."""
        return self._inherit(*base_classes)


    _CACHE_RETURN = 'return_type'
    def _return(self, return_type: type) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_RETURN)
        if is_cached: return cached

        if not self._be_callable():
            self.__setcache__(Assertion._CACHE_RETURN, False)
            return False
        
        try:
            result = self.__target(*self.__args_fn, **self.__kwargs_fn)
        except Exception:
            self.__setcache__(Assertion._CACHE_RETURN, False)
            return False
        
        is_result: bool = isinstance(result, return_type)
        self.__setcache__(Assertion._CACHE_RETURN, is_result)
        return is_result

    _CACHE_RETURN_ASYNC = 'return_type_async'
    async def _return_async(self, return_type: type) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_RETURN_ASYNC)
        if is_cached: return cached
        
        if not self._be_callable():
            self.__setcache__(Assertion._CACHE_RETURN_ASYNC, False)
            return False

        try:
            if self.__async_fn:
                result = await self.__target(*self.__args_fn, **self.__kwargs_fn)
            else:
                result = self.__target(*self.__args_fn, **self.__kwargs_fn)
        except Exception:
            self.__setcache__(Assertion._CACHE_RETURN_ASYNC, False)
            return False
        
        is_result: bool = isinstance(result, return_type)
        self.__setcache__(Assertion._CACHE_RETURN_ASYNC, is_result)
        return is_result

    def assert_return(self, message: str, return_type: type) -> Self:
        """Assert that an object returns a certain type."""
        if not self._return(return_type):
            self.__delcache__(Assertion._CACHE_RETURN)
            raise AssertionError(message)
        return self

    async def assert_async_return(self, message: str, return_type: type) -> Self:
        """Assert that an async object returns a certain type."""
        if not await self._return_async(return_type):
            self.__delcache__(Assertion._CACHE_RETURN_ASYNC)
            raise AssertionError(message)
        return self

    def must_return(self, return_type: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object returns a certain type."""
        if not self._return(return_type):
            self.__delcache__(Assertion._CACHE_RETURN)
            raise custom_expt(f'Object {self.__target} does not return {return_type}')

    async def must_async_return(self, return_type: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an async object returns a certain type."""
        if not await self._return_async(return_type):
            self.__delcache__(Assertion._CACHE_RETURN_ASYNC)
            raise custom_expt(f'Object async {self.__target} does not return {return_type}')

    def should_return(self, return_type: type) -> bool:
        """Check that an object returns a certain type."""
        return self._return(return_type)

    async def should_async_return(self, return_type: type) -> bool:
        """Check that an async object returns a certain type."""
        return await self._return_async(return_type)
    

    _CACHE_RAISE = 'raise'
    def _raise(self, exception: type[Exception]) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_RAISE)
        if is_cached: return cached

        try:
            self.__target(*self.__args_fn, **self.__kwargs_fn)
        except exception:
            self.__setcache__(Assertion._CACHE_RAISE, True)
            return True
        except Exception:
            self.__setcache__(Assertion._CACHE_RAISE, False)
            return False
        else:
            self.__setcache__(Assertion._CACHE_RAISE, False)
            return False

    _CACHE_RAISE_ASYNC = 'raise_async'
    async def _raise_async(self, exception: type[Exception]) -> bool:
        cached, is_cached = self.__getcache__(Assertion._CACHE_RAISE_ASYNC)
        if is_cached: return cached

        try:
            if self.__async_fn:
                await self.__target(*self.__args_fn, **self.__kwargs_fn)
            else:
                self.__target(*self.__args_fn, **self.__kwargs_fn)
        except exception:
            self.__setcache__(Assertion._CACHE_RAISE_ASYNC, True)
            return True
        except Exception:
            self.__setcache__(Assertion._CACHE_RAISE_ASYNC, False)
            return False
        else:
            self.__setcache__(Assertion._CACHE_RAISE_ASYNC, False)
            return False

    def assert_raise(self, message: str, exception: type[Exception]) -> Self:
        """Assert that an object raises a certain exception."""
        if not self._raise(exception):
            self.__delcache__(Assertion._CACHE_RAISE)
            raise AssertionError(message)
        return self

    async def assert_async_raise(self, message: str, exception: type[Exception]) -> Self:
        """Assert that an async object raises a certain exception."""
        if not await self._raise_async(exception):
            self.__delcache__(Assertion._CACHE_RAISE_ASYNC)
            raise AssertionError(message)
        return self

    def must_raise(self, exception: type[Exception], custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object raises a certain exception."""
        try:
            self.__target(*self.__args_fn, **self.__kwargs_fn)
        except exception:
            return
        except Exception as e:
            self.__delcache__(Assertion._CACHE_RAISE)
            raise custom_expt(f'Object {self.__target} raised {type(e)} instead of {exception}')
        else:
            self.__delcache__(Assertion._CACHE_RAISE)
            raise custom_expt(f'Object {self.__target} did not raise any exception, expected {exception}')

    async def must_async_raise(self, exception: type[Exception], custom_expt: type[Exception] = TypeError) -> None:
        """Require that an async object raises a certain exception."""
        try:
            if self.__async_fn:
                await self.__target(*self.__args_fn, **self.__kwargs_fn)
            else:
                self.__target(*self.__args_fn, **self.__kwargs_fn)
        except exception:
            return
        except Exception as e:
            self.__delcache__(Assertion._CACHE_RAISE_ASYNC)
            raise custom_expt(f'Object async {self.__target} raised {type(e)} instead of {exception}')
        else:
            self.__delcache__(Assertion._CACHE_RAISE_ASYNC)
            raise custom_expt(f'Object async {self.__target} did not raise any exception, expected {exception}')

    def should_raise(self, exception: type[Exception]) -> bool:
        """Check that an object raises a certain exception."""
        return self._raise(exception)

    async def should_async_raise(self, exception: type[Exception]) -> bool:
        """Check that an async object raises a certain exception."""
        return await self._raise_async(exception)


    _CACHE_BE_ASYNC = 'be_async'
    def _be_async(self) -> bool:
        cached, is_cached = self.__getcache__('be_async')
        if is_cached: return cached

        is_async: bool = self._be_callable() and self.__async_fn
        self.__setcache__('be_async', is_async)
        return is_async

    def assert_be_async(self, message: str) -> Self:
        """Assert that an object is an async function or coroutine."""
        if not self._be_async():
            self.__delcache__(Assertion._CACHE_BE_ASYNC)
            raise AssertionError(message)
        return self

    def must_be_async(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is an async function or coroutine."""
        if not self._be_async():
            self.__delcache__(Assertion._CACHE_BE_ASYNC)
            raise custom_expt(f'Object {self.__target} is not an async function or coroutine')

    def should_be_async(self) -> bool:
        """Check that an object is an async function or coroutine."""
        return self._be_async()

    def can_be_async(self) -> bool:
        """Check if an object can be awaited."""
        return inspect.isawaitable(self.__target)


    _CACHE_BE_CALLABLE = 'be_callable'
    def _be_callable(self) -> bool:
        cached, is_cached = self.__getcache__('be_callable')
        if is_cached: return cached

        is_callable: bool = self.__target_kind in ['function', 'class'] or callable(self.__target)
        self.__setcache__('be_callable', is_callable)
        return is_callable

    def assert_be_callable(self, message: str) -> Self:
        """Assert that an object is callable."""
        if not self._be_callable():
            self.__delcache__(Assertion._CACHE_BE_CALLABLE)
            raise AssertionError(message)
        return self

    def must_be_callable(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is callable."""
        if not self._be_callable():
            self.__delcache__(Assertion._CACHE_BE_CALLABLE)
            raise custom_expt(f'Object {self.__target} is not callable')

    def should_be_callable(self) -> bool:
        """Check that an object is callable."""
        return self._be_callable()


    _CACHE_BE_ITERABLE = 'be_iterable'
    def _be_iterable(self) -> bool:
        cached, is_cached = self.__getcache__('be_iterable')
        if is_cached: return cached

        is_iterable: bool = hasattr(self.__target, '__iter__')
        self.__setcache__('be_iterable', is_iterable)
        return is_iterable

    def assert_be_iterable(self, message: str) -> Self:
        """Assert that an object is iterable."""
        if not self._be_iterable():
            self.__delcache__(Assertion._CACHE_BE_ITERABLE)
            raise AssertionError(message)
        return self
        
    def must_be_iterable(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is iterable."""
        if not self._be_iterable():
            self.__delcache__(Assertion._CACHE_BE_ITERABLE)
            raise custom_expt(f'Object {self.__target} is not iterable')

    def should_be_iterable(self) -> bool:
        """Check that an object is iterable."""
        return self._be_iterable()
    

    _CACHE_BE_DOCUMENTED = 'be_documented'
    def _be_documented(self) -> bool:
        cached, is_cached = self.__getcache__('be_documented')
        if is_cached: return cached

        is_documented: bool = bool(inspect.getdoc(self.__target) or self.__target.__doc__ or self.__target.__annotations__)
        self.__setcache__('be_documented', is_documented)
        return is_documented

    def assert_be_documented(self, message: str) -> Self:
        """Assert that an object is documented."""
        if not self._be_documented():
            self.__delcache__(Assertion._CACHE_BE_DOCUMENTED)
            raise AssertionError(message)
        return self
    
    def must_be_documented(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is documented."""
        if not self._be_documented():
            self.__delcache__(Assertion._CACHE_BE_DOCUMENTED)
            raise custom_expt(f'Object {self.__target} is not documented')

    def should_be_documented(self) -> bool:
        """Check that an object is documented."""
        return self._be_documented()


    async def _be_run_within(self, time_limit: float) -> bool: # does not cache results
        start_time: float = time.perf_counter()

        try:
            if self.__async_fn:
                await asyncio.wait_for(self.__target(*self.__args_fn, **self.__kwargs_fn), timeout=time_limit)
            else:
                self.__target(*self.__args_fn, **self.__kwargs_fn)
        except asyncio.TimeoutError:
            return False
        
        end_time: float = time.perf_counter()
        return (end_time - start_time) < time_limit

    async def assert_be_run_within(self, message: str, time_limit: float) -> Self:
        """Assert that an object executes in less than a certain time limit."""
        if not await self._be_run_within(time_limit):
            raise AssertionError(message)
        return self

    async def must_be_run_within(self, time_limit: float, custom_expt: type[Exception] = TimeoutError) -> None:
        """Require that an object executes in less than a certain time limit in seconds."""
        if not await self._be_run_within(time_limit):
            raise custom_expt(f'Object {self.__target} did not execute in less than {time_limit} seconds')

    async def should_be_run_within(self, time_limit: float) -> bool:
        """Check that an object executes in less than a certain time limit."""
        return await self._be_run_within(time_limit)



def classname(obj: object | Callable | type) -> str:
    """Get the class name of an object."""
    match obj:
        case type() if inspect.isfunction(obj) or inspect.ismethod(obj):
            return obj.__qualname__.split('.')[0]
        case type() if inspect.isclass(obj):
            return obj.__name__
        case _:
            return obj.__class__.__name__

def structure(obj: object) -> dict:
    """Get the structure of an object."""
    return obj.__dict__

def fields(obj: object) -> list[str]:
    """Get the list of fields of an object."""
    return list(obj.__dict__.keys())

def methods(obj: object) -> list[str]:
    """Get the list of methods of an object."""
    return [attr for attr in dir(obj) if callable(getattr(obj, attr)) and not attr.startswith('__')]

def attributes(obj: object) -> list[str]:
    """Get the list of attributes of an object."""
    return [attr for attr in dir(obj) if not callable(getattr(obj, attr)) and not attr.startswith('__')]

