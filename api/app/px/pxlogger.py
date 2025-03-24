from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from decimal import Decimal
from logging import Formatter, Handler, Logger, LogRecord, StreamHandler, getLevelName, getLogger
from os import getenv
from typing import Any, Final, TypedDict, Union
from uuid import UUID, uuid4

from dotenv import load_dotenv
from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers.data import YamlLexer

from app.utils import map_none

load_dotenv()

_IS_LOCAL_LOGGING: Final[bool] = map_none(os.environ.get("LOCAL_LOGGING"), lambda x: x == "TRUE") or False
_LOCAL_LOGGING_COLOR: Final[str] = os.environ.get("LOCAL_LOGGING_COLOR") or "gruvbox-dark"


class PxRecord(ABC):
    @abstractmethod
    def message(self) -> str:
        """
        Provides a message related to a log record.

        Returns:
            a message
        """

    @abstractmethod
    def context(self) -> dict[Any, Any]:
        """
        Provides a context related to a log record.

        The context is a mapping in which keys are searchable fields and
        values are any Python objects representing meaningful information.

        Returns:
            a context
        """


class PxNote(PxRecord):
    __slots__ = ("_text", "_context")

    def __init__(self, text: str, **context: Union[str, Any]) -> None:
        self._text = text
        self._context = context

    def message(self) -> str:
        return self._text

    def context(self) -> dict[Any, Any]:
        return self._context


class PxMonitoringNote(PxNote):
    def __init__(self, text: str, **context: Union[str, Any]) -> None:
        super().__init__(f"Monitoring case! {text}", **context)


class _Encoder(json.JSONEncoder):
    """The class encodes non-serializable objects."""

    def default(self, o: Union[Decimal, UUID, Any]) -> Union[float, Any]:  # Found too short name
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


_context: ContextVar[dict[str, Any]] = ContextVar("session-data", default={})


class _PxJsonMessageRecord(TypedDict, total=False):
    time: str
    location: dict[str, Union[str, int]]
    message: str
    context: dict[str, Any]
    exception: dict[str, Any]


class _PxJsonMessage(TypedDict):
    logger: dict[str, str]
    record: _PxJsonMessageRecord


def _dict_to_str(dct: Mapping[str, Any]) -> list[str]:
    lst = []
    for k, v in dct.items():
        if isinstance(v, Mapping):
            lst.append(f'  "{k}":')
            lst.extend("  " + x for x in _dict_to_str(v))
        else:
            lst.append(f'  "{k}": >')
            lst.extend("    " + x for x in str(v).rstrip("\n").split("\n"))
    return lst


class PxJsonFormatter(Formatter):
    def format(self, record: LogRecord) -> str:  # function is too complex
        message: _PxJsonMessage = {
            "logger": {
                "name": record.name,
                "level": record.levelname,
            },
            "record": {
                "time": self._formated_time(record),
                "location": {
                    "path": record.pathname,
                    "line": record.lineno,
                },
                "message": record.msg.message() if isinstance(record.msg, PxRecord) else record.getMessage(),
            },
        }
        context: dict[str, Any] = {}
        if isinstance(record.msg, PxRecord) and record.msg.context():
            context.update(record.msg.context())
        if _context.get():
            context.update(_context.get())
        if context:
            message["record"]["context"] = context
        if exception_data := self._formatted_exception(record):
            message["record"]["exception"] = exception_data
        if _IS_LOCAL_LOGGING:
            msg = "\n".join(_dict_to_str(message))
            output = f"""\
PxNote:
{msg}"""
            return highlight(output, YamlLexer(), TerminalTrueColorFormatter(style=_LOCAL_LOGGING_COLOR))
        try:
            # ``default=str`` handles TypeError that could be raised for the complex objects.
            # ``cls=_Encoder`` handles some complex types.
            return json.dumps(message, default=str, cls=_Encoder)
        except Exception as ex:  # noqa
            # In the case of any exception, try manual JSON formatting and preserve an error for the analytic.
            message["logger"]["error"] = str(ex)
            return str(message).replace("'", '"')

    def _formated_time(self, record: LogRecord) -> str:
        """
        Formats a creation time of the record.

        The format is ISO format with milliseconds and timezone offset like ``2022-08-30T23:53:22.158-04:00``.

        Args:
            record: a log record

        Returns:
            ISO format string
        """
        return datetime.fromtimestamp(record.created, timezone.utc).astimezone().isoformat(timespec="milliseconds")

    def _formatted_exception(self, record: LogRecord) -> dict[str, Any]:
        """
        Formats an exception that is attached to the record.

        Args:
            record: a log record

        Returns:
            exception data
        """
        exc_info = record.exc_info
        if not exc_info:
            return {}
        details = {
            "message": str(exc_info[1]),
            # "__name__" is not a known member of "None"
            "type": exc_info[0].__name__,  # type: ignore
            "stacktrace": self.formatException(exc_info),
        }
        record.exc_info = None
        record.exc_text = None
        return details


class PxContextAction(ABC):
    @abstractmethod
    def updated_context(self, current_context: dict[str, Any]) -> dict[str, Any]:
        """
        Provides an updated context to use.

        The method should return a new context instead of modifying ``current_context``.

        Args:
            current_context: the current context

        Returns:
            a new updated context
        """


class _PxContextSetAction(PxContextAction):
    def __init__(self, **kwargs: Union[str, Any]) -> None:
        self._data = kwargs

    def updated_context(self, current_context: dict[str, Any]) -> dict[str, Any]:
        new_context = current_context.copy()
        new_context.update(self._data)
        return new_context


class _PxContextDropAction(PxContextAction):
    def __init__(self, *key_for_removal: str) -> None:
        self._keys_for_removal = key_for_removal

    def updated_context(self, current_context: dict[str, Any]) -> dict[str, Any]:
        new_context = current_context.copy()
        for key_to_remove in self._keys_for_removal:
            new_context.pop(key_to_remove)
        return new_context


class _AlwaysEmptyContext(PxContextAction):
    def updated_context(self, current_context: dict[str, Any]) -> dict[str, Any]:
        return {}


class PxContext:  # Found too many methods
    def __init__(self, name: str) -> None:
        self._name = name

    def set(self, value: Union[str, Any]) -> PxContextAction:
        return _PxContextSetAction(**{self._name: value})

    @classmethod
    def set_empty(cls) -> PxContextAction:
        return _AlwaysEmptyContext()

    @classmethod
    def set_multiple(cls, **kwargs: Union[str, Any]) -> PxContextAction:
        return _PxContextSetAction(**kwargs)

    def drop(self) -> PxContextAction:
        return _PxContextDropAction(self._name)

    @classmethod
    def drop_multiple(cls, *keys_for_removal: str) -> PxContextAction:
        return _PxContextDropAction(*keys_for_removal)

    @classmethod
    def sensor(cls) -> PxContext:
        return cls("sensor")

    @classmethod
    def hub(cls) -> PxContext:
        return cls("hub")

    @classmethod
    def client(cls) -> PxContext:
        return cls("client")

    @classmethod
    def email(cls) -> PxContext:
        return cls("email")

    @classmethod
    def request(cls) -> PxContext:
        return cls("request")

    @classmethod
    def new_request(cls) -> PxContextAction:
        return cls.request().set(str(uuid4()))

    def as_managed(self, value: Union[str, Any]) -> PxManagedContext:
        return PxManagedContext(self, value)


class PxManagedContext:
    def __init__(self, context: PxContext, value: Union[str, Any]) -> None:
        self._context = context
        self._value = value

    def set(self) -> PxContextAction:
        return self._context.set(self._value)

    def drop(self) -> PxContextAction:
        return self._context.drop()


class _EnhancedLogger(Logger):
    """
    The class adds context management capabilities for the standard ``Logger`` class.

    This will be configured as a default logger class for the ``logging`` module.
    """

    def alter_context(self, *actions: PxContextAction) -> None:
        for next_action in actions:
            _context.set(next_action.updated_context(_context.get()))

    @contextmanager
    def with_context(self, *contexts: PxManagedContext) -> Generator[_EnhancedLogger, None, None]:
        """
        Manages given context automatically when used in a context manager (``with`` statement).

        While creating a context manager with ``_logger.with_context``, the managed context(s) (``PxManagedContext``)
        could be passed as the initial ones. Within the context, ``_logger.alter_context`` allows managing additional
        contexts using actions (``PxContextAction```).

        The original context that was before the context manager creation (``with`` statement) will be restored
        regardless of the way how it (context) was changed.

        Example:
            There is a need to loop over a list of sensors. So, the sensor context should be added at the beginning of
             a loop and removed at the end.

            >>> _logger = PxLogger(__name__)
            >>> for sensor in sensors:
            >>>     _logger.alter_context(PxContext.sensor().set(sensor))
            >>>     # logic, logging statements, context modifications
            >>>     _logger.alter_context(PxContext.sensor().drop())

            As the last line could be forgotten, the last processed sensor will be in the context of further records.
            And ``with_context`` solves this problem.

            >>> _logger = PxLogger(__name__)
            >>> for sensor in sensors:
            >>>     with _logger.with_context(PxManagedContext(PxContext.sensor(), sensor)):
            >>>         # logic, logging statements, context modifications

        Args:
            contexts: context(s) to manage

        Yields:
            a logger instance
        """
        origin_context = _context.get()
        self.alter_context(*[context.set() for context in contexts])
        yield self
        _context.set(origin_context)


# configure the default logger class
Logger.manager.setLoggerClass(_EnhancedLogger)


class PxLogger(_EnhancedLogger):
    """
    The main class for logger objects creation.

    This class acts as a factory that

    1. creates a logger object with  ``logging.getLogger`` method
    2. configures created logger with proper logging level

    """

    def __new__(  # pyright: ignore
        cls,
        name: str,  # B008 Do not perform function calls in argument defaults.
        # WPS404 Found complex default value
        # level should be a different type `_Level` which is not accessible
        level: int = getLevelName(getenv("PX_LOGGING_LEVEL", "WARNING")),  # noqa: B008
    ) -> PxLogger:
        """
        Initializes a new instance of the logger.

        By default, the ``level`` is set to ``WARNING``. However, if there is ``PX_LOGGING_LEVEL`` environment
        variable set, it will override the level - recommended way.

        Args:
            name: a name of the logger
            level: a logging level (one of CRITICAL, ERROR, WARNING, INFO, DEBUG; see ``logging.INFO``, etc.)

        Returns:
            a configured logger object
        """
        origin = getLogger(name)
        origin.setLevel(level)
        return origin  # type: ignore


LoggingLevel = int


def configure_logger(
    logger: Logger,
    /,
    # B008 Do not perform function call `getLevelName` in argument defaults
    logging_level: LoggingLevel = getLevelName(getenv("PX_LOGGING_LEVEL", "WARNING")),  # noqa: B008
    handler: Handler = StreamHandler(),  # noqa: B008
    *handlers: Handler,
) -> None:
    """
    Configures a logger with defined output(s) that utilizes standard formatting.

    The logging configuration does the following:
    1. removes any existing handlers
    2. configures given output(s)/handler(s) with the standard ``PxJsonFormatter`` and required logging level
    3. assign configured handler(s) to the logger

    Why are handlers removed? This gives full control on how the logging happens as often it is preconfigured.
    For instance, Lambda has its own default handler. And if one more has been added, the logs will be written twice.
    To get more read https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda.

    By default, any logger will be reconfigured for writing into standard output with ``WARNING`` level. If there is
    the ``PX_LOGGING_LEVEL`` environment variable set, it will override the level - it's a recommended way.

    Args:
        logger: a logger that should be reconfigured
        logging_level: a logging level for the logger
        handler: main output
        handlers: additional outputs if more than one is required

    """
    if logger.handlers:
        for log_handler in logger.handlers:
            logger.removeHandler(log_handler)
    handler.setFormatter(PxJsonFormatter())
    logger.addHandler(handler)
    for other in handlers:
        other.setFormatter(PxJsonFormatter())
        logger.addHandler(other)
    logger.setLevel(logging_level)


def configure_root_logger(
    # B008 Do not perform function call `getLevelName` in argument defaults
    handler: Handler = StreamHandler(),  # noqa: B008
    level: LoggingLevel = getLevelName(getenv("PX_LOGGING_LEVEL", "WARNING")),  # noqa: B008
) -> None:
    """
    Configures the root logger.

    By default, the log records will be written to the standard output.

    For getting consistent logging, it's recommended to reconfigure all external loggers using ``configure_logger``.
    The code below will suit for most cases:

    >>> from logging import WARNING, Logger, root
    >>> from src.px.pxlogger import configure_logger, configure_root_logger
    >>> configure_root_logger()
    >>> for logger in root.manager.loggerDict.values():
    >>>     if not isinstance(logger, Logger):
    >>>         continue
    >>>     configure_logger(logger, logging_level=WARNING)
    """
    configure_logger(getLogger(), logging_level=level, handler=handler)
