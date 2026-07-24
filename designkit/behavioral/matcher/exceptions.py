
class SearcherException(Exception):
    """Base class for all searcher errors."""
    pass

class MatcherException(Exception):
    """Base class for all matcher errors."""
    pass



class NoMatchError(SearcherException):
    """Raised when no match is found."""

    def __init__(self, pattern: str, value: str) -> None:
        super().__init__(f'No match found for pattern [{pattern}] in value: {value}.')
        self.pattern: str = pattern
        self.value: str = value

class NoWasMatchedError(SearcherException):
    """Raised when no match was found for a given value."""

    def __init__(self, value: str) -> None:
        super().__init__(f'Searcher has no match for value {value}.')
        self.value: str = value

class MatchNotFoundError(SearcherException):
    """Raised when no match was found for a given value."""

    def __init__(self, value: str, catch: str | None = None) -> None:
        super().__init__(f'No match was found for value {value}' + (f' with catch: {catch}' if catch else '.'))
        self.value: str = value
        self.catch: str | None = catch



class NoCasesMatchedError(MatcherException):
    """Raised when no cases are matched in the matcher."""

    def __init__(self, value: str) -> None:
        super().__init__(f'No cases matched for value: {value}')
        self.value: str = value

class UnsupportedTypeError(MatcherException):
    """Raised when an unsupported type is encountered in the matcher."""

    def __init__(self, method: str, type: type) -> None:
        super().__init__(f'Unsupported type {type} for the method: {method}.')
        self.method: str = method
        self.type: type = type

class RecursionLimitExceededError(MatcherException):
    """Raised when the recursion limit is exceeded in the matcher."""

    def __init__(self, value: str, max_recursions: int) -> None:
        super().__init__(f'Recursion limit exceeded for value: {value}; {max_recursions} recursions was raised.')
        self.value: str = value
        self.max_recursions: int = max_recursions
