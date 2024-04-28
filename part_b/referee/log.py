# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from enum import Enum
from time import time
from typing import Any, Callable
from inspect import signature


class LogColor(Enum):
    """
    An `enum` capturing the ANSI color codes for console output.
    """
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET_ALL = "\033[0m"

    def __str__(self):
        return self.value

    def __value__(self):
        return self.value


class LogLevel(Enum):
    """
    An `enum` capturing the log levels for any given log stream.
    """
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    def __int__(self):
        return self.value

    def __lt__(self, other):
        return int(self) < int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

def default_handler(message: str):
    print(message)

class LogStream:
    """
    A simple logging stream class for handling log messages with different
    levels of verbosity and output settings.
    """
    _start_time = None
    _max_namespace_length = 0
    _global_settings = {
        "level": LogLevel.DEBUG,
        "handlers": [default_handler],
        "ansi": True,
        "unicode": True,
        "color": LogColor.RESET_ALL,
        "output_time": False,
        "output_namespace": True,
        "output_level": True,
    }

    def __init__(self, 
        namespace: str, 
        color: LogColor | None = None, 
        level: LogLevel | None = None,
        handlers: list[Callable] | None = None,
        unicode: bool | None = None,
        ansi: bool | None = None,
        output_time: bool | None = None,
        output_namespace: bool | None = None,
        output_level: bool | None = None,
        adjust_namespace_length: bool | None = True
    ):

        self._namespace = namespace
        if color is not None:
            self._color = color
        if level is not None:
            self._level = level
        if handlers is not None:
            self._handlers = handlers.copy()
        if unicode is not None:
            self._unicode = unicode
        if ansi is not None:
            self._ansi = ansi
        if output_time is not None:
            self._output_time = output_time
        if output_namespace is not None:
            self._output_namespace = output_namespace
        if output_level is not None:
            self._output_level = output_level
        if adjust_namespace_length is not None:
            self._adjust_namespace_length = adjust_namespace_length

        # Consistent start time for all log streams
        LogStream._start_time = LogStream._start_time or time() 

        # Consistent namespace length for all log streams
        if self._adjust_namespace_length:
            LogStream._max_namespace_length = max(
                LogStream._max_namespace_length,
                len(self._namespace)
            )

    @classmethod
    def set_global_setting(cls, key: str, value: Any):
        cls._global_settings[key] = value

    def setting(self, key: str) -> Any:
        # Return local settings if they exist, otherwise return global settings
        return getattr(self, f"_{key}", LogStream._global_settings[key])
    
    def log(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        Log a message with a dynamic level of verbosity.
        """
        message_lines = message.splitlines()
        for line in message_lines:
            line_base_content = \
                f"{self._s_namespace()}"\
                f"{self._s_time()}"\
                f"{self._s_level(level)}"
            line_base = \
                f"{self._s_color_start()}"\
                f"{line_base_content}"\
                f"{self._s_color_end()}"
            self._out(line_base + line, level)

    def _out(self, message: str, level: LogLevel):
        # Optionally strip unicode symbols
        if not self.setting("unicode"):
            message = message.encode("ascii", "ignore").decode()

        for handler in self.setting("handlers"):
            # If handler takes a level argument, pass it
            if "level" in signature(handler).parameters:
                handler(message, level)
            else:
                handler(message)

    def debug(self, message=""):
        """
        Log a debug message.
        """
        if self.setting("level") <= LogLevel.DEBUG:
            self.log(message, LogLevel.DEBUG)

    def info(self, message=""):
        """
        Log an informational message.
        """
        if self.setting("level") <= LogLevel.INFO:
            self.log(message, LogLevel.INFO)

    def warning(self, message=""):
        """
        Log a warning message.
        """
        if self.setting("level") <= LogLevel.WARNING:
            self.log(message, LogLevel.WARNING)
    
    def error(self, message=""):
        """
        Log an error message.
        """
        if self.setting("level") <= LogLevel.ERROR:
            self.log(message, LogLevel.ERROR)

    def critical(self, message=""):
        """
        Log a critical message.
        """
        # Always print critical messages
        self.log(message, LogLevel.CRITICAL)

    def _s_time(self) -> str:
        if not self.setting("output_time"):
            return ""

        update_time = time() - (LogStream._start_time or 0)
        return f"T{update_time:06.2f} "

    def _s_namespace(self) -> str:
        if not self.setting("output_namespace"):
            return ""

        return f"* {self._namespace:<{LogStream._max_namespace_length}} "

    def _s_level(self, level = LogLevel.INFO) -> str:
        if not self.setting("output_level"):
            return ""

        return {
            LogLevel.DEBUG: "~",
            LogLevel.INFO: ":",
            LogLevel.WARNING: "#",
            LogLevel.ERROR: "!",
            LogLevel.CRITICAL: "@"
        }[level] + " "

    def _s_color_start(self) -> str:
        if not self.setting("ansi"):
            return ""

        return f"{self.setting('color')}"

    def _s_color_end(self) -> str:
        if not self.setting("ansi"):
            return ""

        return f"{LogColor.RESET_ALL}"

class NullLogger(LogStream):
    """
    A simple null logger that does not log anything. Can be used to disable
    logging wherever a LogStream is expected.
    """
    def __init__(self):
        super().__init__("null", None, LogLevel.ERROR)

    def log(self, *_):
        pass
