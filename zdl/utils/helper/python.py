import functools
from typing import Tuple, Union, Type

from zdl.utils.io.log import logger


def except_as_None(exception: Union[Type[Exception], Tuple[Type[Exception]]] = Exception):
    def inner(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                logger.warning(f'{func.__name__}({args} {kwargs}) -> {e.__str__()}',
                               extra={'func_name': 'except_as_None'})
                return None

        return wrap

    return inner
