
from pathlib import Path
from typing import Callable, Self
import pynput


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end: bool = False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}( children={list(self.children.keys())}, is_end={self.is_end} )'

class Trie:
    def __init__(self) -> None:
        self.__root = TrieNode()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}( root={self.__root} )'

    def __repr__(self) -> str:
        def walk(node: TrieNode | None, acc: str) -> list[str]:
            if node is None:
                return []
            
            words: list[str] = []
            if node.is_end:
                words.append(acc)

            for char, child in node.children.items():
                words.extend(walk(child, acc + char))
            
            return words
        
        return ', '.join(walk(self.__root, ''))

    def __len__(self) -> int:
        return self.coincidences

    def __contains__(self, word: str) -> bool:
        return self.exists(word)

    def __call__(self, prefix: str) -> list[str]:
        if not isinstance(prefix, str):
            raise TypeError(f"Expected a string, got {type(prefix).__name__}")
    
        return self.words_with_prefix(prefix)

    def __getitem__(self, prefix: tuple[str]) -> list[str]:
        if not isinstance(prefix, tuple):
            raise TypeError(f"Expected a tuple, got {type(prefix).__name__}")
        
        return self.words_with_prefix(''.join(prefix))

    @classmethod
    def with_list(cls, words: list[str]) -> Trie:
        trie: Trie = cls()
        for word in words:
            trie.insert(word)
        return trie

    @classmethod
    def with_file(cls, file_path: Path) -> Trie:
        trie: Trie = cls()
        with open(file_path, 'r') as file:
            for line in file:
                word: str = line.strip()
                trie.insert(word)
        return trie
    
    def insert(self, word: str) -> None:
        node: TrieNode = self.__root

        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        node.is_end = True
    
    def traverse(self, prefix: str) -> TrieNode | None:
        node: TrieNode | None = self.__root

        for char in prefix:
            node = node.children.get(char)
            if node is None:
                return None
        
        return node

    def clear(self) -> None:
        self.__root = TrieNode()

    def exists(self, word: str) -> bool:
        node: TrieNode | None = self.traverse(word)
        return node is not None and node.is_end
    
    def starts_with(self, prefix: str) -> bool:
        return self.traverse(prefix) is not None
    
    def words_with_prefix(self, prefix: str) -> list[str]:
        payload: list[str] = []

        def walk(node: TrieNode | None, acc: str) -> None:
            if node is None:
                return
            
            if node.is_end:
                payload.append(acc)

            for char, child in node.children.items():
                walk(child, acc + char)

        walk(self.traverse(prefix), prefix)
        return payload

    def search(self, word: str) -> str:
        possible_words: list[str] = self.words_with_prefix(word)

        if not possible_words:
            raise ValueError(f"No words found with prefix '{word}'")
        
        return possible_words[0]

    @property
    def is_empty(self) -> bool:
        return not bool(self.__root.children)

    @property
    def root(self) -> TrieNode:
        return self.__root

    @property
    def coincidences(self) -> int:
        def count(node: TrieNode | None) -> int:
            if node is None:
                return 0
            
            total: int = 1 if node.is_end else 0

            for child in node.children.values():
                total += count(child)
            
            return total
        
        return count(self.__root)

class TrieIterator:
    def __init__(self, trie: Trie) -> None:
        self.__trie: Trie = trie
        self.__words: list[str] = self.__trie.words_with_prefix('')
        self.__index: int = 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> str:
        if self.__index < len(self.__words):
            word: str = self.__words[self.__index]
            self.__index += 1
            return word
        else:
            raise StopIteration()

    def __len__(self) -> int:
        return len(self.__words)

    @property
    def trie(self) -> Trie:
        return self.__trie

    @property
    def words(self) -> list[str]:
        return self.__words

    @property
    def index(self) -> int:
        return self.__index

    @property
    def has_next(self) -> bool:
        return self.__index < len(self.__words)


def autocomplete(trie: Trie, on_update: Callable[[str, list[str]], None], buffer: str = '', *, esc_key_stops: bool = False, enter_key_clears: bool = False) -> None:
    def _on_press(key: pynput.keyboard.Key | pynput.keyboard.KeyCode) -> None:
        nonlocal buffer
        try:
            match key:
                case pynput.keyboard.Key.backspace:
                    buffer = buffer[:-1]
                case pynput.keyboard.Key.space:
                    buffer += ' '
                case pynput.keyboard.Key.esc if esc_key_stops:
                    return False
                case _ if key.char is not None:
                    buffer += key.char
                case pynput.keyboard.Key.enter if enter_key_clears:
                    buffer = ''
                case _:
                    return

            suggestions: list[str] = trie.words_with_prefix(buffer)
            on_update(buffer, suggestions)
            
        except AttributeError:
            pass

    with pynput.keyboard.Listener(on_press=_on_press) as listener:
        listener.join()

