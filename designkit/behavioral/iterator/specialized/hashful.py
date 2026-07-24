
from typing import Any, Callable, Iterable

from ..core import Iterator
from ..exceptions import (
    NoMoreItemsError,
    NotStartedYetError,
    DecryptNotImplementedError
)
from ..iter_types import IteratorBase

class HashIterator[I, H: str | Any](IteratorBase):
    def __init__(
            self,
            collection: Iterable[I],
            encrypt_func: Callable[[I], H],
            decrypt_func: Callable[[H], I] | None = None
        ) -> None:

        self.__encrypter: Callable[[I], H] = encrypt_func
        self.__decrypter: Callable[[H], I] | None = decrypt_func
        
        self.__collection: list[I] = [
            self.__encrypter(item)
            for item
            in collection
        ]

        self.__iterator: Iterator[H] = Iterator(self.__collection)



    def __str__(self) -> str:
        return f"{self.__class__.__name__}( {len(self)} total items, {self.__iterator.size()} remaining )"
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"    length={len(self.__collection)}, "
            f"    index={self.__iterator.index}, "
            f"    remaining={self.__iterator.remaining}"
            f")"
        )



    def __iter__(self) -> HashIterator[I]:
        return self

    def __next__(self) -> H:
        if self.__iterator.index >= len(self.__collection):
            raise NoMoreItemsError(self) from StopIteration
        return self.next()
    


    def __len__(self) -> int:
        return self.size()
    
    def size(self) -> int:
        return len(self.__collection)
    
    
    
    def is_empty(self) -> bool:
        return self.__iterator.is_empty()
    
    def has_next(self) -> bool:
        return self.__iterator.has_next()



    def append(self, item: I) -> None:
        encrypted_item: H = self.__encrypter(item)
        self.__iterator.append(encrypted_item)

    def copy(self) -> HashIterator[I, H]:
        return HashIterator(self.__collection, self.__encrypter, self.__decrypter)



    def peek(self) -> H:
        # precatch the exception before to confirm the action
        # so, this code is double-executed
        if self.__iterator.index >= len(self.__collection):
            raise NoMoreItemsError(self) from StopIteration
        return self.__iterator.peek()

    def next(self) -> H:
        return self.__iterator.next()
    
    def rollback(self) -> None:
        self.__iterator.rollback()


    
    @property
    def current(self) -> H:
        # precatch the exception before to confirm the action
        # so, this code is double-executed
        if self.__iterator.index == 0:
            raise NotStartedYetError(self)
        return self.__iterator.current

    @property
    def index(self) -> int:
        return self.__iterator.index
    
    @property
    def remaining(self) -> int:
        return self.__iterator.remaining



    def encrypt(self, item: I, *args: Any, **kwargs: Any) -> H:
        return self.__encrypter(item, *args, **kwargs)

    def decrypt(self, hash_value: H, *args: Any, **kwargs: Any) -> I:
        if self.__decrypter is None:
            raise DecryptNotImplementedError()
        return self.__decrypter(hash_value, *args, **kwargs)
