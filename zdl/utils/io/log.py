import logging
import os
from enum import Enum

import sys

import colorlog

# usage:
#   1. use default logger:
#       from zdl.utils.io.log import logger
#   2. change all logger in project, as default logger = orgLogger, it is non-color:
#       from zdl.utils.io import log;log.theme('dark');from zdl.utils.io.log import logger
#       !!should be placed in front of other imports which imported log module.
#   3. change single file logger mode:
#       from zdl.io.log import darkThemeColorLogger as logger


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


class Level(Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = WARN = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = FATAL = logging.CRITICAL


def theme(theme_='dark'):
    global logger
    ref_count = sys.getrefcount(logger)
    logger.info(f'logger ref count: {ref_count}')
    if ref_count > 4:
        logger.warning('You can only change loggers in other modules, before they are imported!')
    if theme_ == 'dark':
        logger = darkThemeColorLogger
    elif theme_ == 'light':
        logger = lightThemeColorLogger
    elif theme_ == 'original':
        logger = orgLogger
    else:
        logger.error('theme should be in ["dark", "light", "original"]!')


def configConsoleLogger(level):
    # 当同时存在console和file logger时，单独设置console。一般情况直接logger.setLevel即可。
    # 为了避免麻烦，将color和非color设置合并
    for h in logger.handlers + darkThemeColorLogger.handlers + lightThemeColorLogger.handlers:
        if not isinstance(h, logging.FileHandler):
            h.setLevel(level)


def addFileLogger(file, level=logging.DEBUG, mode='w'):
    # 为了避免麻烦，将color和非color设置合并
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            if handler.baseFilename == os.path.abspath(file):
                return
    file_handler = logging.FileHandler(file, mode, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_FILE_FORMAT))
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
    darkThemeColorLogger.addHandler(file_handler)
    lightThemeColorLogger.addHandler(file_handler)


def localFileLogger(file, level=logging.DEBUG, mode='w'):
    local_file_logger = logging.getLogger(file)
    if len(local_file_logger.handlers) == 0:
        file_handler = logging.FileHandler(file, mode, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(_FILE_FORMAT))
        file_handler.setLevel(level)
        local_file_logger.addHandler(file_handler)
    return local_file_logger


def _test():
    logger.debug('')
    logger.info('')
    logger.warning('')
    logger.error('')
    logger.critical('')


logging.root.setLevel(logging.DEBUG)

_consoleHandler = logging.StreamHandler()
_consoleHandler.setFormatter(logging.Formatter(_CONSOLE_FORMAT, _DATEFMT_SHORT))
_consoleHandler.setLevel(logging.DEBUG)

orgLogger = logging.getLogger('main')
# logger.setLevel(logging.DEBUG)
orgLogger.addHandler(_consoleHandler)
orgLogger.propagate = False

_darkColorConsoleHandler = colorlog.StreamHandler()
_darkColorConsoleHandler.setFormatter(
    colorlog.ColoredFormatter(_COLOR_CONSOLE_FORMAT, _DATEFMT_SHORT,
                              log_colors=_DARK_THEME_COLORS,
                              secondary_log_colors=_DARK_SECONDARY_LOG_COLORS))

darkThemeColorLogger = colorlog.getLogger('color.dark')
darkThemeColorLogger.addHandler(_darkColorConsoleHandler)
darkThemeColorLogger.propagate = False

_lightColorConsoleHandler = colorlog.StreamHandler()
_lightColorConsoleHandler.setFormatter(
    colorlog.ColoredFormatter(_COLOR_CONSOLE_FORMAT, _DATEFMT_SHORT,
                              log_colors=_LIGHT_THEME_COLORS,
                              secondary_log_colors=_LIGHT_SECONDARY_LOG_COLORS))

lightThemeColorLogger = colorlog.getLogger('color.light')
lightThemeColorLogger.addHandler(_lightColorConsoleHandler)
lightThemeColorLogger.propagate = False

logger = orgLogger
