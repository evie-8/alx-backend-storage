#!/usr/bin/env python3
"""Using Redis"""

import uuid
import redis
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """akes a single method Callable argument
    and returns a Callable."""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper function"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """A function that stores
    the history of inputs and outputs"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper for the decorated function"""
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output

    return wrapper


def replay(func: Callable):
    '''replay'''
    r = redis.Redis()
    key = func.__qualname__
    input = r.lrange("{}:inputs".format(key), 0, -1)
    output = r.lrange("{}:outputs".format(key), 0, -1)
    calls_number = len(input)
    times_str = 'times'
    if calls_number == 1:
        times_str = 'time'
    fin = '{} was called {} {}:'.format(key, calls_number, times_str)
    print(fin)
    for k, v in zip(input, output):
        fin = '{}(*{}) -> {}'.format(
            key_m,
            k.decode('utf-8'),
            v.decode('utf-8')
        )
        print(fin)


class Cache():
    '''class Cache'''
    def __init__(self):
        '''initializer of cache instance'''
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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
