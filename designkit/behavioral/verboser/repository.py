
import logging
from contextlib import nullcontext
from designkit.behavioral.typing import Assertion, classname
from rich.status import Status
from rich.console import Console
from rich import get_console


console: Console = get_console()

COLOR_INFO      = 'green'
COLOR_WARNING   = '#FF9800'
COLOR_ERROR     = '#F44336'
COLOR_DEBUG     = '#2196F3'
SYMBOL_INFO     = '\\[i] '
SYMBOL_WARNING  = '\\[W] '
SYMBOL_ERROR    = '\\[E] '
SYMBOL_DEBUG    = '\\[D] '


class VerboseSystem:
    def __init__(self, verbose: bool = True, *, logger: logging.Logger = logging.getLogger(__name__), is_dev: bool = False) -> None:
        if not isinstance(verbose, bool):
            raise ValueError('verbose must be a boolean')
        if not isinstance(logger, logging.Logger):
            raise ValueError('logger must be an instance of logging.Logger')
        if not isinstance(is_dev, bool):
            raise ValueError('is_dev must be a boolean')

        self.__verbose: bool = verbose
        self.__is_dev: bool = is_dev
        self.__logger: logging.Logger = logger
    
    def __str__(self) -> str:
        return f'{classname(self)}( verbose={self.__verbose} | id={id(self)} )'

    def __repr__(self) -> str:
        return f'{classname(self)}( verbose={self.__verbose} | id={id(self)} )'

    def __bool__(self) -> bool:
        return self.__verbose

    def __neg__(self) -> bool:
        return not self.__verbose

    def _raise_exception(self, expt: Exception | None) -> None:
        if expt is not None and self.__is_dev:
            raise expt

    @staticmethod
    def _format_message(message: str, expt: Exception | None = None) -> str:
        if expt is None:
            return message
        return f'{message} Details: {expt}'

    def _emit(
        self,
        level: int,
        message: str,
        style: str = '',
        expt: Exception | None = None,
    ) -> None:
        formatted_message: str = self._format_message(message, expt)
        self.__logger.log(level, formatted_message)
        if style:
            console.print(f'[{style}]{formatted_message}[/{style}]')
            return
        console.print(formatted_message)

    def just_log(self, message: str, style: str = '') -> None:
        """ Custom log with style, ignoring the verbose flag. """
        self._emit(logging.INFO, message, style)

    def log(self, message: str, style: str = '') -> None:
        """ Custom log with style, only if verbose is enabled. """
        if self.__verbose:
            self._emit(logging.INFO, message, style)

    def log_status(self, message: str, style: str = '') -> Status | nullcontext:
        """ Custom log with style for status messages, only if verbose is enabled. """
        if self.__verbose:
            self.__logger.info(message)
            status_message: str = f'[{style}]{message}[/{style}]' if style else message
            return console.status(status_message)
        return nullcontext()


    def just_info(self, message: str) -> None:
        """ Log the message unconditionally, ignoring the verbose flag. """
        self._emit(logging.INFO, SYMBOL_INFO + message, COLOR_INFO)

    def info(self, message: str) -> None:
        if self.__verbose:
            self._emit(logging.INFO, SYMBOL_INFO + message, COLOR_INFO)

    def info_status(self, message: str) -> Status | nullcontext:
        if self.__verbose:
            self.__logger.info(message)
            return console.status(f'[{COLOR_INFO}]{SYMBOL_INFO}{message}[/{COLOR_INFO}]')
        return nullcontext()


    def just_warning(self, message: str, warn: Exception | None = None) -> None:
        """ Log the warning message unconditionally, ignoring the verbose flag. """
        self._emit(logging.WARNING, SYMBOL_WARNING + message, COLOR_WARNING, warn)
        self._raise_exception(warn)
    
    def warning(self, message: str, warn: Exception | None = None) -> None:
        if self.__verbose:
            self._emit(logging.WARNING, SYMBOL_WARNING + message, COLOR_WARNING, warn)
        self._raise_exception(warn)

    def warning_status(self, message: str, warn: Exception | None = None) -> Status | nullcontext:
        if self.__verbose:
            self._emit(logging.WARNING, '\\[W] ' + message, COLOR_WARNING, warn)
            self._raise_exception(warn)
            return console.status(f'[{COLOR_WARNING}]{SYMBOL_WARNING}{message}[/{COLOR_WARNING}]')
        self._raise_exception(warn)
        return nullcontext()

    def just_error(self, message: str, expt: Exception | None = None) -> None:
        """ Log the error message unconditionally, ignoring the verbose flag. """
        self._emit(logging.ERROR, SYMBOL_ERROR + message, COLOR_ERROR, expt)
        self._raise_exception(expt)

    def error(self, message: str, expt: Exception | None = None) -> None:
        if self.__verbose:
            self._emit(logging.ERROR, SYMBOL_ERROR + message, COLOR_ERROR, expt)
        self._raise_exception(expt)

    def error_status(self, message: str, expt: Exception | None = None) -> Status | nullcontext:
        if self.__verbose:
            self._emit(logging.ERROR, '\\[E] ' + message, COLOR_ERROR, expt)
            self._raise_exception(expt)
            return console.status(f'[{COLOR_ERROR}]{SYMBOL_ERROR}{message}[/{COLOR_ERROR}]')
        self._raise_exception(expt)
        return nullcontext()


    def just_debug(self, message: str) -> None:
        """ Log the debug message unconditionally, ignoring the verbose flag. """
        self._emit(logging.DEBUG, SYMBOL_DEBUG + message, COLOR_DEBUG)

    def debug(self, message: str) -> None:
        if self.__verbose:
            self._emit(logging.DEBUG, SYMBOL_DEBUG + message, COLOR_DEBUG)

    def debug_status(self, message: str) -> Status | nullcontext:
        if self.__verbose:
            self.__logger.debug(SYMBOL_DEBUG + message)
            return console.status(f'[{COLOR_DEBUG}]{SYMBOL_DEBUG}{message}[/{COLOR_DEBUG}]')
        return nullcontext()


    def set_verbose(self, verbose: bool) -> VerboseSystem:
        Assertion(verbose).must_be(bool)
        self.__verbose = verbose
        return self

    @property
    def is_verbose(self) -> bool:
        return self.__verbose
