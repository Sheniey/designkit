
import os, dotenv
from typing import Any, Callable, Literal, Self
from enum import StrEnum
from functools import wraps
from designkit.structural.environment.exceptions import (
    EnvironmentMachineException,
    InvalidEnvironmentModeError
)


class EnvMode(StrEnum):
    DEVELOPMENT = 'development'
    PRODUCTION = 'production'
    TESTING = 'testing'

type Environment = Literal[
    'development', 'dev',
    'production', 'prod', 'build',
    'testing', 'test'
] | EnvMode


class EnvironmentMachine:
    __feat_metavar__: str = '__is_forbidden_feature__'
    __dotenv_preloaded__: bool = False

    def __init__(self, environment: Environment) -> None:
        self.__env: EnvMode = self._normalize_envmode(environment)
        self.__fallback: Callable[[Callable, EnvMode, list[Any], dict[str, Any]], None] | None = None

    @staticmethod
    def _normalize_envmode(env: Environment) -> EnvMode:
        try:
            return {
                'development':  EnvMode.DEVELOPMENT,
                'dev':          EnvMode.DEVELOPMENT,
                'production':   EnvMode.PRODUCTION,
                'prod':         EnvMode.PRODUCTION,
                'build':        EnvMode.PRODUCTION,
                'testing':      EnvMode.TESTING,
                'test':         EnvMode.TESTING,
                EnvMode.DEVELOPMENT: EnvMode.DEVELOPMENT,
                EnvMode.PRODUCTION:  EnvMode.PRODUCTION,
                EnvMode.TESTING:     EnvMode.TESTING,
            }[env]
        except KeyError as e:
            raise InvalidEnvironmentModeError(env) 

    def _validate_feature(self, feature: Callable, envmode: Environment) -> bool:
        env: EnvMode = self._normalize_envmode(envmode)
        forbidden: bool = env != self.__env
        setattr(feature, EnvironmentMachine.__feat_metavar__, forbidden)
        return forbidden

    def _check_feature(self, feature: Callable) -> bool:
        return getattr(feature, EnvironmentMachine.__feat_metavar__, False)


    @classmethod
    def from_env(cls, mnmonic: str = 'APP_ENVIRONMENT', *, env_path: str = '.env') -> EnvironmentMachine:
        """
        Creates an EnvironmentMachine instance based on the environment variable specified by `mnmonic`.
        
        FIRST : tries to load the environment variables from the specified `.env` file.
        THEN  : reads the environment variable specified by `mnmonic`.
        IF    : the environment variable is not set or contains an invalid value, `raises a ValueError`.
        """
        env: Environment | None = os.getenv(mnmonic, None)
        if not EnvironmentMachine.__dotenv_preloaded__ and env is None:
            EnvironmentMachine.loadenv(path=env_path)
        env = os.getenv(mnmonic, None)

        if env is None:
            raise ValueError(f"Cannot setup the environment mode because the environment variable '{mnmonic}' is not set.")
        return cls(env)


    def only_in[A, K, R](self, envmode: Environment) -> Callable[[A, K], R]:
        """
        Decorator to forbid a feature can be executed in environments other than the specified one.
        Raises a RuntimeError if the feature is forbidden in the current environment.
        """
        normalized_env: EnvMode = self._normalize_envmode(envmode)

        def decorator(feature: Callable[[A, K], R]) -> Callable[[A, K], R]:
            # before any execution, mark the feature as forbidden if the environment does not match
            self._validate_feature(feature, envmode=normalized_env)

            @wraps(feature)
            def wrapper(*args: A, **kwargs: K) -> R:
                # after any execution, check if the feature is forbidden in the current environment
                if self._check_feature(feature):
                    if self.__fallback is None:
                        raise RuntimeError(f'Feature {feature.__name__} is forbidden in the current environment.')
                    else:
                        self.__fallback(feature, self.__env, list(args), dict(kwargs))
                
                return feature(*args, **kwargs)
            return wrapper
        return decorator

    async def only_async_in[A, K, R](self, envmode: Environment) -> Callable[[A, K], R]:
        """
        Decorator to forbid an asynchronous feature from being executed in environments other than the specified one.
        Raises a RuntimeError if the feature is forbidden in the current environment.
        """
        normalized_env: EnvMode = self._normalize_envmode(envmode)

        def decorator(feature: Callable[[A, K], R]) -> Callable[[A, K], R]:
            # before any execution, mark the feature as forbidden if the environment does not match
            self._validate_feature(feature, envmode=normalized_env)

            @wraps(feature)
            async def wrapper(*args: A, **kwargs: K) -> R:
                # after any execution, check if the feature is forbidden in the current environment
                if self._check_feature(feature):
                    if self.__fallback is None:
                        raise RuntimeError(f'Feature {feature.__name__} is forbidden in the current environment.')
                    else:
                        self.__fallback(feature, self.__env, list(args), dict(kwargs))

                return await feature(*args, **kwargs)
            return wrapper
        return decorator


    def run_in[A, K, R](self, envmode: Environment) -> Callable[[A, K], R | None]:
        """
        Decorator that allows a feature can be executed only if it matches the current environment.
        """
        normalized_env: EnvMode = self._normalize_envmode(envmode)
        
        def decorator(feature: Callable[[A, K], R]) -> Callable[[A, K], R | None]:
            # before any execution, mark the feature as forbidden if the environment does not match
            self._validate_feature(feature, envmode=normalized_env)

            @wraps(feature)
            def wrapper(*args: A, **kwargs: K) -> R | None:
                # after any execution, check if the feature is forbidden in the current environment
                if self._check_feature(feature):
                    return None

                return feature(*args, **kwargs)
            return wrapper
        return decorator

    async def run_async_in[A, K, R](self, envmode: Environment) -> Callable[[A, K], R | None]:
        """
        Decorator that allows an asynchronous feature to be executed only if it matches the current environment.
        """
        normalized_env: EnvMode = self._normalize_envmode(envmode)

        def decorator(feature: Callable[[A, K], R]) -> Callable[[A, K], R | None]:
            # before any execution, mark the feature as forbidden if the environment does not match
            self._validate_feature(feature, envmode=normalized_env)

            @wraps(feature)
            async def wrapper(*args: A, **kwargs: K) -> R | None:
                # after any execution, check if the feature is forbidden in the current environment
                if self._check_feature(feature):
                    return None

                return await feature(*args, **kwargs)
            return wrapper
        return decorator


    @staticmethod
    def loadenv(path: str = '.env') -> None:
        dotenv.load_dotenv(path)
        EnvironmentMachine.__dotenv_preloaded__ = True

    @staticmethod
    def findenv(path: str = '.env') -> str:
        return dotenv.find_dotenv(path)

    @staticmethod
    def getenv[T](*mnemonics: str, default: T = None, validate: Callable[[T], bool] = lambda v: True) -> T:
        for mnemonic in mnemonics:
            value: T = os.getenv(mnemonic, default)

            any_value: bool = value is not None
            if any_value and not validate(value):
                raise ValueError(f"Environment variable '{mnemonic}' has an invalid value: {value}")
            if any_value:
                return value
        return default

    @staticmethod
    def setenv(mnemonic: str, value: str) -> None:
        os.environ[mnemonic] = value

    @staticmethod
    def delenv(mnemonic: str) -> None:
        if mnemonic in os.environ:
            del os.environ[mnemonic]

    @staticmethod
    def savenv(path: str = '.env') -> None:
        for key, value in os.environ.items():
            dotenv.set_key(path, key, value)


    def on_forbidden[A, K, R](self, func: Callable[[Callable, EnvMode, A, K], R] = lambda feat, curr_env, *args, **kwargs: print(f" [!] Feature '{feat.__name__}' is forbidden in the environment '{curr_env}'. Continuing execution...")) -> Self:
        """
        A function to be called when a feature is forbidden in the current environment.
        """
        self.__fallback = func
        return self

    def on_begin(self, func: Callable[[EnvMode], None] = lambda env: print(f" [*] Starting environment in '{env}'")) -> Self:
        """
        A function to be called at the beginning of the environment execution.
        """
        func(self.__env)
        return self

    @property
    def environment(self) -> EnvMode:
        return self.__env
