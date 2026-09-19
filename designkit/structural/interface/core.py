
from collections.abc import (
    Hashable as _C_ABC_Hashable,
    Awaitable as _C_ABC_Awaitable,
    Iterator as _C_ABC_Iterator,
    AsyncIterator as _C_ABC_AsyncIterator,
    Iterable as _C_ABC_Iterable,
    AsyncIterable as _C_ABC_AsyncIterable
)
from typing import (
    Any as _Any,
    Protocol as _P,
    runtime_checkable as _runtime_checkable
)


# ================================================== #
# BEHAVIORAL INTERFACES                             #
# ================================================== #

@_runtime_checkable
class Renderable(_P):
    """Interface for objects that can be rendered using the `render()` method."""
    def render(self) -> None:
        ...

@_runtime_checkable
class Updatable(_P):
    """Interface for objects that can be updated using the `update()` method."""
    def update(self) -> None:
        ...

@_runtime_checkable
class Openable(_P):
    """Interface for objects that can be opened using the `open()` method."""
    def open(self) -> None:
        ...

@_runtime_checkable
class Closable(_P):
    """Interface for objects that can be closed using the `close()` method."""
    def close(self) -> None:
        ...

@_runtime_checkable
class Resettable(_P):
    """Interface for objects that can be reset using the `reset()` method."""
    def reset(self) -> None:
        ...

@_runtime_checkable
class Enableable(_P):
    """Interface for objects that can be enabled using the `enable()` and `disable()` methods."""
    def enable(self) -> None:
        ...
    def disable(self) -> None:
        ...

@_runtime_checkable
class Visible(_P):
    """Interface for objects that can be shown or hidden using the `show()` and `hide()` methods."""
    def show(self) -> None:
        ...
    def hide(self) -> None:
        ...

@_runtime_checkable
class Collapsible(_P):
    """Interface for objects that can be collapsed or expanded using the `collapse()` and `expand()` methods."""
    def collapse(self) -> None:
        ...
    def expand(self) -> None:
        ...

@_runtime_checkable
class Playable(_P):
    """Interface for objects that can be played, paused, or stopped using the `play()`, `pause()`, and `stop()` methods."""
    def play(self) -> None:
        ...
    def pause(self) -> None:
        ...
    def stop(self) -> None:
        ...

@_runtime_checkable
class Drawable(_P):
    """Interface for objects that can be drawn using the `draw()` method."""
    def draw(self) -> None:
        ...

@_runtime_checkable
class Draggable(_P):
    """Interface for objects that can be dragged using the `drag()` method."""
    def drag(self) -> None:
        ...

@_runtime_checkable
class Resizable(_P):
    """Interface for objects that can be resized using the `resize()` method."""
    def resize(self) -> None:
        ...

@_runtime_checkable
class Selectable(_P):
    """Interface for objects that can be selected using the `select()` method."""
    def select(self) -> None:
        ...

@_runtime_checkable
class Focusable(_P):
    """Interface for objects that can be focused or blurred using the `focus()` and `blur()` methods."""
    def focus(self) -> None:
        ...
    def blur(self) -> None:
        ...

@_runtime_checkable
class Serializable(_P):
    """Interface for objects that can be serialized and deserialized using the `serialize()` and `deserialize()` methods."""
    def serialize(self) -> _Any:
        ...
    def deserialize(self, data: _Any):
        ...

@_runtime_checkable
class Initializable(_P):
    """Interface for objects that can be initialized using the `initialize()` method."""
    def initialize(self) -> None:
        ...

@_runtime_checkable
class Interactive(_P):
    """Interface for objects that can handle interactions using the `handle_event()` method."""
    def handle_event(self, event: _Any) -> bool:
        ...

@_runtime_checkable
class Disposable(_P):
    """Interface for objects that can be disposed using the `dispose()` method."""
    def dispose(self) -> None:
        ...

@_runtime_checkable
class AsyncDisposable(_P):
    """Interface for objects that can be asynchronously disposed using the `async dispose()` method."""
    async def dispose(self) -> None:
        ...

@_runtime_checkable
class Translatable(_P):
    """Interface for objects that can be translated using the `translate()` method."""
    def translate(self) -> None:
        ...

@_runtime_checkable
class Copyable(_P):
    """Interface for objects that can be copied using the `copy()` method."""
    def copy(self) -> _Any:
        ...

@_runtime_checkable
class DeepCopyable(_P):
    """Interface for objects that can be deep copied using the `deep_copy()` method."""
    def deep_copy(self) -> _Any:
        ...

@_runtime_checkable
class Subscribable(_P):
    """Interface for objects that can handle subscriptions using the `subscribe()` and `unsubscribe()` methods."""
    def subscribe(self) -> None:
        ...
    def unsubscribe(self) -> None:
        ...

@_runtime_checkable
class Emittable(_P):
    """Interface for objects that can emit events using the `emit()` method."""
    def emit(self) -> None:
        ...

@_runtime_checkable
class Sendable(_P):
    """Interface for objects that can send messages using the `send()` method."""
    def send(self) -> None:
        ...

@_runtime_checkable
class Receivable(_P):
    """Interface for objects that can receive messages using the `receive()` method."""
    def receive(self) -> None:
        ...

@_runtime_checkable
class Connectable(_P):
    """Interface for objects that can establish connections using the `connect()` and `disconnect()` methods."""
    def connect(self) -> None:
        ...
    def disconnect(self) -> None:
        ...

@_runtime_checkable
class Graphable(_P):
    """Interface for objects that can be represented as a graph using the `to_graph()` method."""
    def to_graph(self) -> _Any:
        ...

@_runtime_checkable
class Plottable(_P):
    """Interface for objects that can be represented as a plot using the `plot()` method."""
    def plot(self) -> _Any:
        ...

@_runtime_checkable
class Parsable(_P):
    """Interface for objects that can be parsed using the `parse()` method."""
    def parse(self) -> None:
        ...

@_runtime_checkable
class Computable(_P):
    """Interface for objects that can perform computations using the `compute()` method."""
    def compute(self) -> _Any:
        ...

@_runtime_checkable
class Optimizable(_P):
    """Interface for objects that can be optimized using the `optimize()` method."""
    def optimize(self) -> None:
        ...

@_runtime_checkable
class Loadable(_P):
    """Interface for objects that can be loaded using the `load()` method."""
    def load(self) -> None:
        ...


# ================================================== #
# EVENT INTERFACES                                   #
# ================================================== #

@_runtime_checkable
class Clickable(_P):
    """Interface for objects that can handle click events using the `on_click()` and `on_double_click()` methods."""
    def on_click(self) -> None:
        ...
    def on_double_click(self) -> None:
        ...

@_runtime_checkable
class Hoverable(_P):
    """Interface for objects that can handle hover events using the `on_hover_enter()` and `on_hover_exit()` methods."""
    def on_hover_enter(self) -> None:
        ...
    def on_hover_exit(self) -> None:
        ...

@_runtime_checkable
class KeyboardListener(_P):
    """Interface for objects that can handle keyboard events using the `on_key_down()` and `on_key_up()` methods."""
    def on_key_down(self) -> None:
        ...
    def on_key_up(self) -> None:
        ...

@_runtime_checkable
class MouseListener(_P):
    """Interface for objects that can handle mouse events using the `on_mouse_down()`, `on_mouse_up()`, and `on_mouse_move()` methods."""
    def on_mouse_down(self) -> None:
        ...
    def on_mouse_up(self) -> None:
        ...
    def on_mouse_move(self) -> None:
        ...


# ================================================== #
# EVENT INTERFACES                                   #
# ================================================== #

@_runtime_checkable
class HasValueProp(_P):
    """Interface for objects that have a value accessible via the `value` property."""
    @property
    def value(self) -> _Any:
        ...

@_runtime_checkable
class HasIdProp(_P):
    """Interface for objects that have an ID accessible via the `id` property."""
    @property
    def id(self) -> _Any:
        ...


# ================================================== #
# MATHEMATICAL INTERFACES                            #
# ================================================== #

@_runtime_checkable
class Vectorizable(_P):
    """Interface for objects that can be converted to a vector using the `to_vector()` method."""
    def to_vector(self) -> _Any:
        ...

@_runtime_checkable
class Matrixable(_P):
    """Interface for objects that can be converted to a matrix using the `to_matrix()` method."""
    def to_matrix(self) -> _Any:
        ...

@_runtime_checkable
class Transformable(_P):
    """Interface for objects that can be transformed using the `transform()` method."""
    def transform(self) -> None:
        ...

@_runtime_checkable
class Scalable(_P):
    """Interface for objects that can be scaled using the `scale()` method."""
    def scale(self) -> None:
        ...

@_runtime_checkable
class Rotatable(_P):
    """Interface for objects that can be rotated using the `rotate()` method."""
    def rotate(self, angle: _Any) -> None:
        ...

@_runtime_checkable
class Reflectable(_P):
    """Interface for objects that can be reflected using the `reflect()` method."""
    def reflect(self) -> None:
        ...

@_runtime_checkable
class Shearable(_P):
    """Interface for objects that can be sheared using the `shear()` method."""
    def shear(self) -> None:
        ...

@_runtime_checkable
class Skewable(_P):
    """Interface for objects that can be skewed using the `skew()` method."""
    def skew(self) -> None:
        ...

@_runtime_checkable
class Collidable(_P):
    """Interface for objects that can collide using the `collide()` method."""
    def collide(self) -> None:
        ...

@_runtime_checkable
class Movable(_P):
    """Interface for objects that can be moved using the `move()` method."""
    def move(self, delta: _Any) -> None:
        ...


# ================================================== #
# TYPICAL INTERFACES                                 #
# ================================================== #

@_runtime_checkable
class Stackable(_P):
    """Interface for objects that behave like a stack, supporting `push()` and `pop()` methods."""
    def push(self) -> None:
        ...
    def pop(self) -> None:
        ...

@_runtime_checkable
class Queueable(_P):
    """Interface for objects that behave like a queue, supporting `enqueue()` and `dequeue()` methods."""
    def enqueue(self) -> None:
        ...
    def dequeue(self) -> None:
        ...

@_runtime_checkable
class Dequeable(_P):
    """Interface for objects that behave like a deque, supporting `append()`, `appendleft()`, `pop()`, and `popleft()` methods."""
    def append(self) -> None:
        ...
    def appendleft(self) -> None:
        ...
    def pop(self) -> None:
        ...
    def popleft(self) -> None:
        ...

@_runtime_checkable
class GetSetDeletable(_P):
    """Interface for objects that support getting, setting, and deleting attributes using the `get()`, `set()`, and `delete()` methods."""
    def get(self) -> None:
        ...
    def set(self) -> None:
        ...
    def delete(self) -> None:
        ...


# ================================================== #
# METAMETHOD INTERFACES                              #
# ================================================== #

@_runtime_checkable
class Callable(_P):
    """Interface for callable objects that can be invoked using the `call` syntax."""
    def __call__(self) -> None:
        ...

@_runtime_checkable
class Awaitable(_C_ABC_Awaitable[_Any]):
    """Interface for objects that can be awaited using the `await` syntax."""
    ...

@_runtime_checkable
class Iterable(_C_ABC_Iterable[_Any]):
    """Interface for iterable objects that can be iterated over using the `for-in` syntax."""
    ...

@_runtime_checkable
class AsyncIterable(_C_ABC_AsyncIterable[_Any]):
    """Interface for asynchronous iterable objects that can be iterated over using the `async for-in` syntax."""
    ...

@_runtime_checkable
class Iterator(_C_ABC_Iterator[_Any]):
    """Interface for iterator objects that provide the next item in a sequence using the `next()` function."""
    ...

@_runtime_checkable
class AsyncIterator(_C_ABC_AsyncIterator[_Any]):
    """Interface for asynchronous iterator objects that provide the next item in a sequence using the `async for-in` syntax."""
    ...

@_runtime_checkable
class Container(_P):
    """Interface for container objects that support membership tests using the `in` keyword."""
    def __contains__(self, item: _Any) -> bool:
        ...

@_runtime_checkable
class Indexable(_P):
    """Interface for objects that support indexing using the `square bracket` syntax."""
    def __getitem__(self, index: _Any) -> _Any:
        ...
    def __setitem__(self, index: _Any, value: _Any) -> None:
        ...
    def __delitem__(self, index: _Any) -> None:
        ...

@_runtime_checkable
class Attributable(_P):
    """Interface for objects that support attribute access using the dot syntax."""
    def __getattr__(self, name: str) -> _Any:
        ...
    def __setattr__(self, name: str, value: _Any) -> None:
        ...
    def __delattr__(self, name: str) -> None:
        ...

@_runtime_checkable
class Sized(_P):
    """Interface for objects that have a size and support the `len()` function."""
    def __len__(self) -> int:
        ...

@_runtime_checkable
class Convertible(_P):
    """Interface for objects that can provide their type through various `type conversion` methods."""
    def __int__(self) -> int: ...
    def __float__(self) -> float: ...
    def __str__(self) -> str: ...
    def __bool__(self) -> bool: ...
    def __complex__(self) -> complex: ...
    def __bytes__(self) -> bytes: ...

@_runtime_checkable
class Hashable(_C_ABC_Hashable):
    """Interface for objects that can be hashed using the `hash()` function."""
    ...

@_runtime_checkable
class Equatable(_P):
    """Interface for objects that support equality comparisons like `==` and `!=` operators."""
    def __eq__(self, other: _Any) -> bool:
        ...
    def __ne__(self, other: _Any) -> bool:
        ...

@_runtime_checkable
class Comparable(_P):
    """Interface for objects that support rich comparison like `<`, `<=`, `>`, `>=`, `==`, and `!=` operators."""
    def __lt__(self, other: _Any) -> bool: ...
    def __le__(self, other: _Any) -> bool: ...
    def __gt__(self, other: _Any) -> bool: ...
    def __ge__(self, other: _Any) -> bool: ...
    def __eq__(self, other: _Any) -> bool: ...
    def __ne__(self, other: _Any) -> bool: ...

@_runtime_checkable
class Formattable(_P):
    """Interface for objects that support custom string formatting using the `format()` function."""
    def __format__(self, format_spec: str) -> str:
        ...

@_runtime_checkable
class Reprable(_P):
    """Interface for objects that provide a string representation using the `repr()` function."""
    def __repr__(self) -> str:
        ...

@_runtime_checkable
class Debuggable(_P):
    """Interface for objects that provide detailed debugging information through `repr()`, `str()`, and `format()`."""
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def __format__(self, format_spec: str) -> str:
        ...

@_runtime_checkable
class ContextManager(_P):
    """Interface for objects that can be used as context managers with the `with` statement."""
    def __enter__(self) -> _Any:
        ...
    def __exit__(self, exc_type: _Any, exc_value: _Any, traceback: _Any) -> None:
        ...

@_runtime_checkable
class AsyncContextManager(_P):
    """Interface for objects that can be used as asynchronous context managers with the `async with` statement."""
    async def __aenter__(self) -> _Any:
        ...
    async def __aexit__(self, exc_type: _Any, exc_value: _Any, traceback: _Any) -> None:
        ...

@_runtime_checkable
class Operable(_P):
    """Interface for objects that support basic arithmetic operations like `ADD`, `SUB`, `MUL`, `DIV`, `FLOOR-DIV`, `MOD`, and `POWER`."""
    def __add__(self, other: _Any) -> _Any: ...
    def __radd__(self, other: _Any) -> _Any: ...
    def __sub__(self, other: _Any) -> _Any: ...
    def __rsub__(self, other: _Any) -> _Any: ...
    def __mul__(self, other: _Any) -> _Any: ...
    def __rmul__(self, other: _Any) -> _Any: ...
    def __truediv__(self, other: _Any) -> _Any: ...
    def __rtruediv__(self, other: _Any) -> _Any: ...
    def __floordiv__(self, other: _Any) -> _Any: ...
    def __rfloordiv__(self, other: _Any) -> _Any: ...
    def __mod__(self, other: _Any) -> _Any: ...
    def __rmod__(self, other: _Any) -> _Any: ...
    def __pow__(self, other: _Any) -> _Any: ...
    def __rpow__(self, other: _Any) -> _Any: ...

@_runtime_checkable
class BitwiseOperable(_P):
    """Interface for objects that support bitwise operations like `INVERSION`, `AND`, `OR`, `XOR`, `L-SHIFT`, and `R-SHIFT`."""
    def __invert__(self) -> _Any: ...
    def __and__(self, other: _Any) -> _Any: ...
    def __rand__(self, other: _Any) -> _Any: ...
    def __or__(self, other: _Any) -> _Any: ...
    def __ror__(self, other: _Any) -> _Any: ...
    def __xor__(self, other: _Any) -> _Any: ...
    def __lshift__(self, other: _Any) -> _Any: ...
    def __rlshift__(self, other: _Any) -> _Any: ...
    def __rshift__(self, other: _Any) -> _Any: ...
    def __rrshift__(self, other: _Any) -> _Any: ...

@_runtime_checkable
class WeirdOperable(_P):
    """Interface for objects that support unusual or less common arithmetic operations like `MATMUL` and `DIVMOD`."""
    def __matmul__(self, other: _Any) -> _Any: ...
    def __rmatmul__(self, other: _Any) -> _Any: ...
    def __divmod__(self, other: _Any) -> _Any: ...
    def __rdivmod__(self, other: _Any) -> _Any: ...

@_runtime_checkable
class Negatable(_P):
    """Interface for objects that support unary operations like `NEG`, `POS`, and `ABS`."""
    def __neg__(self) -> _Any:
        ...
    def __pos__(self) -> _Any:
        ...
    def __abs__(self) -> _Any:
        ...

@_runtime_checkable
class Reversible(_P):
    """Interface for objects that support the `reversed()` function."""
    def __reversed__(self) -> _Any:
        ...

