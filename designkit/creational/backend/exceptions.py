
class CodecException(Exception):
    """Exception raised for codec errors."""
    pass


class CodecDependencyUnavailable(Exception):
    """Exception raised when a required codec dependency is unavailable."""
    def __init__(self, codec: str, dep_name: str) -> None:
        self.codec: str = codec
        self.dependency_name: str = dep_name
        self.message: str = f'The codec "{codec}" requires the dependency "{dep_name}" which is unavailable; please install the required dependency.'
        super().__init__(self.message)

class CodecDecodeError(Exception):
    """Exception raised for codec decoding errors."""
    pass

class CodecEncodeError(Exception):
    """Exception raised for codec encoding errors."""
    pass
