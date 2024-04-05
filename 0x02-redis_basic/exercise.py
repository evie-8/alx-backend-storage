#!/usr/bin/env python3
"""Using Redis"""

import uuid
import redis
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """function that counts calls to Cache"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """the wrapper class"""
        key_name = method.__qualname__
        self._redis.incr(key_name, 0) + 1
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    '''tore the history of inputs and
    outputs for a particular function.'''

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        ''' def wrapper'''
        key_m = method.__qualname__
        inp = key_m + ':inputs'
        out = key_m + ":outputs"
        data = str(args)
        self._redis.rpush(inp, data)
        fin = method(self, *args, **kwargs)
        self._redis.rpush(out, str(fin))
        return fin
    return wrapper


def replay(func: Callable):
    '''to display the history of calls of a particular function.'''
    red = redis.Redis()
    key = func.__qualname__
    inp = red.lrange("{}:inputs".format(key), 0, -1)
    out = red.lrange("{}:outputs".format(key), 0, -1)
    calls_number = len(inp)
    times_str = 'times'
    if calls_number == 1:
        times_str = 'time'
    fin = '{} was called {} {}:'.format(key, calls_number, times_str)
    print(fin)
    for k, v in zip(inp, out):
        fin = '{}(*{}) -> {}'.format(
            key,
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
