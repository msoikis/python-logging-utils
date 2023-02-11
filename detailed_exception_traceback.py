
"""
This module is intended for easier debugging by printing more detailed and custom exception,
including local vars on each stack trace.


Execute on program start (i.e. main.py):
sys.excepthook = handle_uncaught_exception
To set detailed exception print on uncaught exceptions.


To make logger.exception() log custom exception, setup custom exception handler:
def custom_exception(msg: str, *args, **kwargs):
    _original_logger_exception(msg + get_custom_exc_str(), *args, **kwargs)

_original_logger_exception = logger.exception
logger.exception = custom_exception


If you use your own exception-handler (i.e. FastApi exception-handler), call get_custom_exception_traceback() from
your exception-handler to get detailed message with local vars.


In pytest, add the following function in conftest:
def pytest_exception_interact(node, call, report):
    exc_msg = get_detailed_exception_traceback(call.excinfo.value)
    logger.exception(f'Custom Exception Details:\n{exc_msg}\n')

"""

import logging
import sys
import traceback
from types import TracebackType
from typing import Iterable
from typing import Type


EXCLUDED_TRACES_DEFAULT = (
    'site-packages',
    'log_function_call',
)

EXCLUDED_LOCALS_DEFAULT = (
    ' at 0x',
    '<class ',
    '__',
    '(No symbol)',
)


def handle_uncaught_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> None:
    # To call python's default exception handler, call: sys.__excepthook__(exc_type, exc_value, exc_traceback)
    logger = logging.getLogger()
    logger.exception(get_custom_exc_str(exc_value))


def get_custom_exc_str(exc=None) -> str:
    if exc is None:
        exc_type, exc, tb = sys.exc_info()
    exc_msg = get_custom_exception_traceback(exc)
    return f"\nCustom Exception Message for {repr(exc)}: \n{exc_msg}\n"


def get_custom_exception_traceback(
    exc: BaseException, *,
    excluded_traces: tuple[str, ...] = EXCLUDED_TRACES_DEFAULT,
    excluded_locals: tuple[str, ...] = EXCLUDED_LOCALS_DEFAULT
) -> str:
    tb = traceback.TracebackException.from_exception(exc, capture_locals=True)
    stack_traces = _filter_out_str(tb.format(), excluded_traces)
    full_debug_str = ''.join(stack_traces)
    filtered_lines = _filter_out_str(full_debug_str.splitlines(), excluded_locals)
    debug_str = '\n'.join(filtered_lines)
    return debug_str


def _filter_out_str(str_iter: Iterable[str], exclude_list: Iterable[str]) -> Iterable[str]:
    for string in str_iter:
        if not _is_any_in_str(string, exclude_list):
            yield string


def _is_any_in_str(string: str, str_list: Iterable[str]) -> bool:
    for item in str_list:
        if item in string:
            return True
    return False
