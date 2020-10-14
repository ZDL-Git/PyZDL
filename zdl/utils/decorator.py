import functools
from typing import Tuple, Union


def except_as_None(exception: Union[Exception, Tuple[Exception]] = Exception):
    def inner(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception:
                return None

        return wrap

    return inner
