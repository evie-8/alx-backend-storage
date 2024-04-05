#!/usr/bin/env python3
"""Using Redis"""

import uuid
import redis
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """function that counts calls to Cache"""

    @wraps(method)
    def wrapper(*args, **kwargs):
        """the wrapper class"""
        args[0]._redis.incr(method.__qualname__)
        return method(*args, **kwargs)
    return wrapper


class Cache():
    '''class Cache'''
    def __init__(self):
        '''initializer of cache instance'''
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''generates a key and stores input data'''
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Union[str, bytes, int, float]:
        ''' def get and fn which converts bakc to desired format'''
        value = self._redis.get(key)
        return value if not fn else fn(value)

    def get_int(self, key):
        '''returns int value'''
        return self.get(key, int)

    def get_str(self, key):
        '''returns string value'''
        value = self._redis.get(key)
        return value.decode("utf-8")
