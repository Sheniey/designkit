
class EnvironmentMachineException(Exception):
    """Base exception class for EnvironmentMachine errors.""" 
    pass


class InvalidEnvironmentModeError(EnvironmentMachineException, ValueError):
    """Exception raised for invalid environment modes."""
    def __init__(self, env: str) -> None:
        self.envmode: str = env
        self.message: str = f'Invalid environment mode {env}. Valid modes are development, production, and testing.'
        super().__init__(self.message)
