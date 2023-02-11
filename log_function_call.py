import asyncio
import functools
import logging
from collections.abc import Callable


def log_function_call(logger: logging.Logger, level=logging.DEBUG, log_none_return=True) -> Callable:
    def log_wrapper(func: Callable) -> Callable:
        def log_after(result):
            if result is None and not log_none_return:
                return result
            logger.log(level, f'{func.__name__} returns {result}')
            return result

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                logger.log(level, f'{func.__name__} {args}, {kwargs}')
                try:
                    result = await func(*args, **kwargs)
                except Exception as exc:
                    logger.log(logging.ERROR, f'Exception in {func.__name__} {args}, {kwargs}: {exc.__repr__()}')
                    raise
                return log_after(result)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logger.log(level, f'{func.__name__} {args}, {kwargs}')
                try:
                    result = func(*args, **kwargs)
                except Exception as exc:
                    logger.log(level, f'{exc.__repr__()}')
                    raise
                return log_after(result)
        return wrapper
    return log_wrapper
