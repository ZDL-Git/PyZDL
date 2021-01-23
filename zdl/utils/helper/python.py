import functools
from collections import UserDict
from numbers import Number
from typing import Tuple, Union, Type, Dict

from zdl.utils.io.log import logger


def raise_(ex: BaseException):
    raise ex


class UnAssigned:
    pass


class BResult:
    def __init__(self, status: bool, msg=None):
        self.status = status
        self.msg = msg

    def __bool__(self):
        return self.status

    def __str__(self):
        return self.msg


class ZDict(dict):
    """ ZDict supports deep path and multi keys get.
    Please don't use dot in ZDict str key.
    """

    def __init__(self, seq=None, auto_insert=True, **kwargs):
        if seq is None:
            super().__init__(**kwargs)
        else:
            super().__init__(seq, **kwargs)
        self._auto_insert = auto_insert

    def __getitem__(self, item):
        if isinstance(item, Tuple):
            return [self.get(*t) if isinstance(t, Tuple) else self[t] for t in item]
        elif isinstance(item, str):
            if item.__contains__('.'):
                res = UnAssigned
                for t in item.split('.'):
                    res = self[t] if res is UnAssigned else res[t]
                return res
            else:
                return super().__getitem__(item)
        elif isinstance(item, Number):
            return super().__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            if key.__contains__('.'):
                walk = UnAssigned
                paths = key.split('.')
                for i, t in enumerate(paths[:-1]):
                    pos = self if walk is UnAssigned else walk
                    try:
                        walk = pos[t]
                    except KeyError:
                        if self._auto_insert:
                            pos[t] = walk = {}
                        else:
                            raise KeyError('.'.join(paths[:i + 1]))
                    except Exception:
                        if self._auto_insert:
                            raise ValueError(f"can not insert {t} into {type(pos)} '{pos}'.")
                        else:
                            raise KeyError('.'.join(paths[:i + 1]))
                walk[paths[-1]] = value
                return
        if not self._auto_insert and key not in self:
            raise KeyError(key)
        super().__setitem__(key, value)

    def search(self, item):
        ...


class DeepDataClass:
    def __init__(self, mapping: Dict):
        if not isinstance(mapping, self.KeptDict):
            for key, value in mapping.items():
                if isinstance(value, Dict):
                    mapping[key] = self.__class__(value)
        self.mapping = mapping

    def __getattr__(self, item):
        return self.mapping[item]

    class KeptDict(UserDict):
        """ A class that exists just to tell DeepDataClass not to covert this layer.
        """


class ZDecorators:
    @classmethod
    def exceptAsNone(cls, exception: Union[Type[Exception], Tuple[Type[Exception]]] = Exception):
        def inner(func):
            @functools.wraps(func)
            def wrap(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    logger.warning(f'{func.__name__}({args} {kwargs}) -> {e.__str__()}',
                                   extra={'func_name': 'exceptAsNone'})
                    return None

            return wrap

        return inner
