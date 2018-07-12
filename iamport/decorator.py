import functools


def required(required):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not isinstance(required, list):
                raise TypeError('required have to be list type')
            compare = set(required) - kwargs.keys()
            if len(compare) != 0:
                raise KeyError(f'{list(compare)} is required')
            return func(*args, **kwargs)
        return wrapper
    return deco
