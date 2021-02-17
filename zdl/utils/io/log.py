"""Custom logging wrapper.

Example:
    >> from zdl.utils.io.log import logger
    >> logger.theme(logger.Theme.DARK)
    >> logger.file('xxx.log')
    >> logger.error('logger working')

    >> logger = logger.fork(name='local', sync=True)
"""

import logging
import os
from enum import IntEnum, Enum
from typing import Iterator

import colorlog

_CONSOLE_FORMAT = "[%(levelname).1s|%(asctime)s.%(msecs)03d|%(filename)15s:%(lineno)-3s] %(funcName)s(): %(message)s"
_COLOR_CONSOLE_FORMAT = "%(log_color)s[%(levelname).1s|%(asctime)s.%(msecs)03d|%(filename)15s:%(lineno)-3s] %(funcName)s(): %(message_log_color)s%(message)s"
_FILE_FORMAT = "[%(levelname)-7s|%(asctime)s|%(filename)15s:%(lineno)-3s] %(funcName)s(): %(message)s"
_DATEFMT_SHORT = '%M:%S'
_DARK_THEME_COLORS = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}
_DARK_SECONDARY_LOG_COLORS = {
    'message': {
        'DEBUG': 'white',
        'INFO': 'white',
        'WARNING': 'white',
        'ERROR': 'white',
        'CRITICAL': 'white',
    }
}
_LIGHT_THEME_COLORS = {
    'DEBUG': 'black',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}
_LIGHT_SECONDARY_LOG_COLORS = {
    'message': {
        'DEBUG': 'black',
        'INFO': 'black',
        'WARNING': 'black',
        'ERROR': 'black',
        'CRITICAL': 'black',
    }
}


class LoggerProxy:
    class Level(IntEnum):
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = WARN = logging.WARNING
        ERROR = logging.ERROR
        CRITICAL = FATAL = logging.CRITICAL

    class _MyFilter(logging.Filter):
        def filter(self, record):
            if hasattr(record, 'func_name'):  # arg name compat
                record.funcName = record.func_name
            return True

    class Theme(Enum):
        ORIGINAL = logging.Formatter(_CONSOLE_FORMAT, _DATEFMT_SHORT)
        DARK_BG = colorlog.ColoredFormatter(_COLOR_CONSOLE_FORMAT, _DATEFMT_SHORT,
                                            log_colors=_DARK_THEME_COLORS,
                                            secondary_log_colors=_DARK_SECONDARY_LOG_COLORS)
        LIGHT_BG = colorlog.ColoredFormatter(_COLOR_CONSOLE_FORMAT, _DATEFMT_SHORT,
                                             log_colors=_LIGHT_THEME_COLORS,
                                             secondary_log_colors=_LIGHT_SECONDARY_LOG_COLORS)

    def __init__(self, name='main', level=Level.DEBUG, global_=True, theme=Theme.ORIGINAL):
        self._global = global_
        self._theme = theme

        self._logger = self._getBaseLogger(name)
        self.config(name=name, level=level, theme=theme)
        self._registerDIWEC(self._logger)

    def _getBaseLogger(self, name):
        org_logger = logging.getLogger(name)
        org_logger.addHandler(logging.StreamHandler())
        org_logger.addFilter(self._MyFilter())
        return org_logger

    def _registerDIWEC(self, logger):
        logger = logger or self._logger
        self.debug = logger.debug
        self.info = logger.info
        self.warn = self.warning = logger.warning
        self.error = logger.error
        self.critical = self.fatal = logger.critical

    @property
    def level(self):
        return self._logger.level

    @property
    def _iter_file_handlers(self) -> Iterator[logging.FileHandler]:
        for h in self._logger.handlers:
            if h.__class__ == logging.FileHandler:
                yield h

    @property
    def _iter_console_handlers(self) -> Iterator[logging.StreamHandler]:
        for h in self._logger.handlers:
            if h.__class__ == logging.StreamHandler:
                yield h

    @property
    def name(self):
        return self._logger.name

    def theme(self, theme: Theme):
        self._theme = theme
        for h in self._iter_console_handlers:
            h.setFormatter(theme.value)

    def is_global(self):
        return self._global

    def file(self, file: str, level: Level = None, mode: str = 'w'):
        """
        Arguments:
            mode:
                'w'：覆盖
                'a': 追加
        """
        for handler in self._iter_file_handlers:
            if handler.baseFilename == os.path.abspath(file):
                handler.setLevel(level)
                handler.mode = mode
                return
        file_handler = logging.FileHandler(file, mode, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(_FILE_FORMAT))
        if level:
            file_handler.setLevel(level)
        self._logger.addHandler(file_handler)

    def config(self, name: str = None, level: Level = None, theme: Theme = None, pid: bool = None,
               console_level: Level = None, file_level: Level = None,
               close_stdout: bool = None, close_file: bool = None):
        if name is not None:
            self._logger.name = name
        if level:
            self._logger.setLevel(level)
        if theme:
            self.theme(theme)
        if pid:
            pass

        if console_level:
            for h in self._iter_console_handlers:
                h.setLevel(console_level)
        if close_stdout:
            for h in self._iter_console_handlers:
                self._logger.removeHandler(h)
        if file_level:
            for h in self._iter_file_handlers:
                h.setLevel(file_level)
        if close_file:
            for h in self._iter_file_handlers:
                self._logger.removeHandler(h)

    def fork(self, name, sync=True):
        if self.name == name:
            self._outputError('fork logger name is same as parent, return old logger!!')
            return self

        new = self.__class__(name, global_=False)
        if sync:
            def sync_config(src: LoggerProxy, dst: LoggerProxy):
                for src_console_handler in src._iter_console_handlers:
                    for dst_console_handler in dst._iter_console_handlers:
                        dst_console_handler.setFormatter(src_console_handler.formatter)
                    break

            sync_config(self, new)
        return new

    def _outputError(self, m):
        error_print = self.error if hasattr(self, 'error') else print
        error_print(m)

    def _test(self, m=None):
        m = f'{self.name} logger testing.' if m is None else m
        self.debug(m)
        self.info(m)
        self.warning(m)
        self.error(m)
        self.critical(m)


logging.root.setLevel(logging.DEBUG)
logger = LoggerProxy()
