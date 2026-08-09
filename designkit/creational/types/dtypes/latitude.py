
import validators

class Latitude:
    def __init__(self, value: float):
        if not validators.latitude(value):
            raise ValueError(f"Invalid latitude value: {value}")
        self.value = value
