
class SingletonError(Exception):
    pass

class ItsNotAClassError(SingletonError):
    def __init__(self, obj: object) -> None:
        super().__init__(f"Expected a class, but got an instance of {type(obj).__name__}.")
