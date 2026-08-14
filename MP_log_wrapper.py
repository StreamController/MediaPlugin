"""
Plugin-level logging wrapper for MediaPlugin.

Provides a configurable logger that can be controlled independently of the parent application's
log level, allowing fine-grained control over MediaPlugin's log output.
"""

from loguru import logger as _loguru_logger
import sys

# Log levels from highest to lowest severity
LOG_LEVELS = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "INFO": 20,
    "DEBUG": 10,
    "TRACE": 5,
}

# Current log level for the plugin
_current_log_level = "INFO"


class PluginLogger:
    """Wrapper around loguru logger with plugin-level configuration."""
    
    def __init__(self):
        self._logger = _loguru_logger
    
    def _should_log(self, level: str) -> bool:
        """Check if a message at the given level should be logged."""
        level_value = LOG_LEVELS.get(level.upper(), 20)
        current_value = LOG_LEVELS.get(_current_log_level.upper(), 20)
        return level_value >= current_value
    
    def trace(self, message: str, *args, **kwargs):
        """Log a trace level message."""
        if self._should_log("TRACE"):
            self._logger.trace(message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log a debug level message."""
        if self._should_log("DEBUG"):
            self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log an info level message."""
        if self._should_log("INFO"):
            self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log a warning level message."""
        if self._should_log("WARNING"):
            self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log an error level message."""
        if self._should_log("ERROR"):
            self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log a critical level message."""
        if self._should_log("CRITICAL"):
            self._logger.critical(message, *args, **kwargs)


def set_log_level(level: str) -> None:
    """
    Set the plugin's log level.
    
    Valid levels: CRITICAL, ERROR, WARNING, INFO, DEBUG, TRACE
    
    :param level: The log level to set
    """
    global _current_log_level
    level_upper = level.upper()
    if level_upper not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {level}. Must be one of {list(LOG_LEVELS.keys())}")
    _current_log_level = level_upper


def get_log_level() -> str:
    """Get the current plugin log level."""
    return _current_log_level


# Create the global logger instance
log = PluginLogger()
