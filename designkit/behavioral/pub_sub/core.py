
from typing import Callable, Self
from enum import Enum
from dataclasses import dataclass


@dataclass
class ReasonCallback[R: Enum, T]:
    reason: R
    callback: Callable[[T], None]


class Publisher[R: Enum]:
    def __init__(self, max_subscribers: int | None = None) -> None:
        self.__subscribers: dict[tuple[Suscription, R], Callable] = {}
        self.__max_subscribers = max_subscribers
        self.__subs_count: int = 0

    def __str__(self) -> str:
        return f'{self.__class__.__name__}( subs={len(self.__subscribers)}, max_subs={self.__max_subscribers} )'

    def __len__(self) -> int:
        return self.__subs_count

    def __contains__(self, subscriber: Suscription) -> bool:
        return self.has_subscriber(subscriber)

    def __getitem__(self, subscriber: Suscription) -> list[ReasonCallback[R]]:
        return self.subscribers.get(subscriber, [])

    def __setitem__(self, subscriber: Suscription, reason: R) -> None:
        self.subscribe(subscriber, [reason])

    def subscribe(self, subscriber: Suscription, reasons: list[R]) -> Self:
        if self.__max_subscribers is not None and self.__subs_count >= self.__max_subscribers:
            raise ValueError('Maximum number of subscribers reached')
        
        for reason in reasons:
            expected_callback: str = f'on_{reason.name.lower()}'
            callback: Callable | None = getattr(subscriber, expected_callback)

            if not callable(callback):
                raise ValueError(f'Subscriber must implement a callable method named "{expected_callback}" for reason "{reason.name}"')
            self.__subscribers[(subscriber, reason)] = callback
            self.__subs_count += 1
        return self

    def unsubscribe(self, subscriber: Suscription) -> Self:
        keys_to_remove = [key for key in self.__subscribers if key[0] == subscriber]
        for key in keys_to_remove:
            del self.__subscribers[key]
            self.__subs_count -= 1
        return self

    def unsubscribe_for_reason(self, subscriber: Suscription, reason: R) -> Self:
        key: tuple[Suscription, R] = (subscriber, reason)
        if key in self.__subscribers:
            del self.__subscribers[key]
            self.__subs_count -= 1
        return self

    def notify[T](self, reason: R, content: T) -> Self:
        for (subs, r), callback in self.__subscribers.items():
            if r == reason:
                callback(content)
        return self
    
    def is_subscribed(self, subscriber: Suscription, reason: R) -> bool:
        return (subscriber, reason) in self.__subscribers

    def has_subscriber(self, subscriber: Suscription) -> bool:
        return any(subs == subscriber for (subs, _) in self.__subscribers.keys())

    def has_subs_for_reason(self, reason: R) -> bool:
        return any(r == reason for (_, r) in self.__subscribers.keys())

    @property
    def subscribers(self) -> dict[Suscription, list[ReasonCallback[R]]]:
        result: dict[Suscription, list[ReasonCallback[R]]] = {}
        for (subs, r), callback in self.__subscribers.items():
            if subs not in result:
                result[subs] = []
            result[subs].append(ReasonCallback(reason=r, callback=callback))
        return result

    @subscribers.delete
    def subscribers(self) -> None:
        self.__subscribers.clear()

    @property
    def max_subscribers(self) -> int | None:
        return self.__max_subscribers

class Suscription:
    ...
