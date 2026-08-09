
import inspect, time, asyncio
from typing import Self, Callable, Literal


class Assertion:
    """A class for asserting conditions on objects."""

    def __init__(self, target: object | Callable | type, *args, **kwargs) -> None:
        self.__target: object | Callable | type = target
        self.__target_kind: Literal['class', 'function', 'object'] = 'class' if inspect.isclass(target) else 'function' if callable(target) else 'object'

        self.__async_fn: bool = inspect.iscoroutinefunction(target) or inspect.isasyncgenfunction(target)
        self.__args_fn: tuple = args
        self.__kwargs_fn: dict[str, object] = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}( {self.__target!r} )'

    def __str__(self) -> str:
        return repr(self)

    def _be_void(self) -> bool:
        return self.__target is not None or not self.__target

    def assert_be_void(self, message: str) -> Self:
        """Assert that an object is not None or empty."""
        if not self._be_void():
            raise AssertionError(message)
        return self

    def must_be_void(self, custom_expt: type[Exception] = ValueError) -> None:
        """Require that an object is not None or empty."""
        if not self._be_void():
            raise custom_expt(f'Object {self.__target} is None or empty')

    def should_be_void(self) -> bool:
        """Check that an object is not None or empty."""
        return self._be_void()

    def _be(self, *types: type) -> bool:
        fil_types: list = list(filter(lambda t: t is not None, types))

        if len(fil_types) < len(types) and self.__target is None:
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
            return True
        return False

    def assert_be(self, message: str, *types: type) -> Self:
        """Assert that an object is of a certain type."""
        if not self._be(*types):
            raise AssertionError(message)
        return self

    def must_be(self, *types: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is of a certain type."""
        if not self._be(*types):
            raise custom_expt(f'Object {self.__target} is not one of the following types {", ".join(classname(t) for t in types)}')

    def should_be(self, *types: type) -> bool:
        """Check that an object is of a certain type."""
        return self._be(*types)


    def _have(self, *attributes: str) -> tuple[bool, list[str]]:
        missing = [attr for attr in attributes if not hasattr(self.__target, attr)]
        return not missing, missing

    def assert_have(self, message: str, *attributes: str) -> Self:
        """Assert that an object has certain attributes."""
        has_all, missing = self._have(*attributes)
        if not has_all:
            raise AssertionError(message)
        return self

    def must_have(self, *attributes: str, custom_expt: type[Exception] = AttributeError) -> None:
        """Require that an object has certain attributes."""
        has_all, missing = self._have(*attributes)
        if not has_all:
            raise custom_expt(f'Object {self.__target} does not have attributes {missing}')

    def should_have(self, *attributes: str) -> bool:
        """Check that an object has certain attributes."""
        has_all, _ = self._have(*attributes)
        return has_all


    def _implement(self, *methods: str | Callable) -> tuple[bool, list[str]]:
        get_name = lambda method: method.__name__ if callable(method) else method
        missing = [
            get_name(method)
            for method in methods
            if not callable(getattr(self.__target, get_name(method), None))
        ]
        return not missing, missing

    def assert_implement(self, message: str, *methods: str | Callable) -> Self:
        """Assert that an object implements certain methods."""
        has_all, missing = self._implement(*methods)
        if not has_all:
            raise AssertionError(message)
        return self

    def must_implement(self, *methods: str | Callable, custom_expt: type[Exception] = NotImplementedError) -> None:
        """Require that an object implements certain methods."""
        has_all, missing = self._implement(*methods)
        if not has_all:
            raise custom_expt(f'Object {self.__target} does not implement methods {missing}')

    def should_implement(self, *methods: str | Callable) -> bool:
        """Check that an object implements certain methods."""
        has_all, _ = self._implement(*methods)
        return has_all

    
    def _inherit(self, *base_classes: type) -> bool:
        cls = self.__target if inspect.isclass(self.__target) else type(self.__target)
        return any(issubclass(cls, base) for base in base_classes)

    def assert_inherit(self, message: str, *base_classes: type) -> Self:
        """Assert that an object inherits from certain base classes."""
        if not self._inherit(*base_classes):
            raise AssertionError(message)
        return self

    def must_inherit(self, *base_classes: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object inherits from certain base classes."""
        if not self._inherit(*base_classes):
            raise custom_expt(f'Object {self.__target} does not inherit from {base_classes}')

    def should_inherit(self, *base_classes: type) -> bool:
        """Check that an object inherits from certain base classes."""
        return self._inherit(*base_classes)


    def _return(self, return_type: type) -> bool:
        if not self._be_callable():
            return False

        try:
            result = self.__target(*self.__args_fn, **self.__kwargs_fn)
        except Exception:
            return False
        
        return isinstance(result, return_type)

    async def _return_async(self, return_type: type) -> bool:
        if not self._be_callable():
            return False

        try:
            if self.__async_fn:
                result = await self.__target(*self.__args_fn, **self.__kwargs_fn)
            else:
                result = self.__target(*self.__args_fn, **self.__kwargs_fn)
        except Exception:
            return False
        
        return isinstance(result, return_type)

    def assert_return(self, message: str, return_type: type) -> Self:
        """Assert that an object returns a certain type."""
        if not self._return(return_type):
            raise AssertionError(message)
        return self

    async def assert_async_return(self, message: str, return_type: type) -> Self:
        """Assert that an async object returns a certain type."""
        if not await self._return_async(return_type):
            raise AssertionError(message)
        return self

    def must_return(self, return_type: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object returns a certain type."""
        if not self._return(return_type):
            raise custom_expt(f'Object {self.__target} does not return {return_type}')

    async def must_async_return(self, return_type: type, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an async object returns a certain type."""
        if not await self._return_async(return_type):
            raise custom_expt(f'Object async {self.__target} does not return {return_type}')

    def should_return(self, return_type: type) -> bool:
        """Check that an object returns a certain type."""
        return self._return(return_type)

    async def should_async_return(self, return_type: type) -> bool:
        """Check that an async object returns a certain type."""
        return await self._return_async(return_type)
    

    def _raise(self, exception: type[Exception]) -> bool:
        try:
            self.__target(*self.__args_fn, **self.__kwargs_fn)
        except exception:
            return True
        except Exception:
            return False
        else:
            return False

    async def _raise_async(self, exception: type[Exception]) -> bool:
        try:
            if self.__async_fn:
                await self.__target(*self.__args_fn, **self.__kwargs_fn)
            else:
                self.__target(*self.__args_fn, **self.__kwargs_fn)
        except exception:
            return True
        except Exception:
            return False
        else:
            return False

    def assert_raise(self, message: str, exception: type[Exception]) -> Self:
        """Assert that an object raises a certain exception."""
        if not self._raise(exception):
            raise AssertionError(message)
        return self

    async def assert_async_raise(self, message: str, exception: type[Exception]) -> Self:
        """Assert that an async object raises a certain exception."""
        if not await self._raise_async(exception):
            raise AssertionError(message)
        return self

    def must_raise(self, exception: type[Exception], custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object raises a certain exception."""
        try:
            self.__target(*self.__args_fn, **self.__kwargs_fn)
        except exception:
            return
        except Exception as e:
            raise custom_expt(f'Object {self.__target} raised {type(e)} instead of {exception}')
        else:
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
            raise custom_expt(f'Object async {self.__target} raised {type(e)} instead of {exception}')
        else:
            raise custom_expt(f'Object async {self.__target} did not raise any exception, expected {exception}')

    def should_raise(self, exception: type[Exception]) -> bool:
        """Check that an object raises a certain exception."""
        return self._raise(exception)

    async def should_async_raise(self, exception: type[Exception]) -> bool:
        """Check that an async object raises a certain exception."""
        return await self._raise_async(exception)


    def _be_async(self) -> bool:
        return self._be_callable() and self.__async_fn

    def assert_be_async(self, message: str) -> Self:
        """Assert that an object is an async function or coroutine."""
        if not self._be_async():
            raise AssertionError(message)
        return self

    def must_be_async(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is an async function or coroutine."""
        if not self._be_async():
            raise custom_expt(f'Object {self.__target} is not an async function or coroutine')

    def should_be_async(self) -> bool:
        """Check that an object is an async function or coroutine."""
        return self._be_async()

    def can_be_async(self) -> bool:
        """Check if an object can be awaited."""
        return inspect.isawaitable(self.__target)


    def _be_callable(self) -> bool:
        return self.__target_kind in ['function', 'class'] or callable(self.__target)

    def assert_be_callable(self, message: str) -> Self:
        """Assert that an object is callable."""
        if not self._be_callable():
            raise AssertionError(message)
        return self

    def must_be_callable(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is callable."""
        if not self._be_callable():
            raise custom_expt(f'Object {self.__target} is not callable')

    def should_be_callable(self) -> bool:
        """Check that an object is callable."""
        return self._be_callable()


    def _be_iterable(self) -> bool:
        return hasattr(self.__target, '__iter__')

    def assert_be_iterable(self, message: str) -> Self:
        """Assert that an object is iterable."""
        if not self._be_iterable():
            raise AssertionError(message)
        return self
        
    def must_be_iterable(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is iterable."""
        if not self._be_iterable():
            raise custom_expt(f'Object {self.__target} is not iterable')

    def should_be_iterable(self) -> bool:
        """Check that an object is iterable."""
        return self._be_iterable()
    

    def _be_documented(self) -> bool:
        return bool(inspect.getdoc(self.__target) or self.__target.__doc__ or self.__target.__annotations__)

    def assert_be_documented(self, message: str) -> Self:
        """Assert that an object is documented."""
        if not self._be_documented():
            raise AssertionError(message)
        return self
    
    def must_be_documented(self, custom_expt: type[Exception] = TypeError) -> None:
        """Require that an object is documented."""
        if not self._be_documented():
            raise custom_expt(f'Object {self.__target} is not documented')

    def should_be_documented(self) -> bool:
        """Check that an object is documented."""
        return self._be_documented()


    async def _be_run_within(self, time_limit: float) -> bool:
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
