import functools
import weakref
from datetime import datetime, timedelta


def timed_cache(**timedelta_kwargs):
    def decorator(func):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() - update_delta

        func = functools.lru_cache(None)(func)

        @functools.wraps(func)
        def cached_func(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()

            if now >= next_update:
                func.cache_clear()
                next_update = now + update_delta
            return func(*args, **kwargs)

        return cached_func

    return decorator


def memoized_method(*lru_args, **lru_kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            self_weak = weakref.ref(self)

            @functools.wraps(func)
            @functools.lru_cache(*lru_args, **lru_kwargs)
            def cached_method(*args, **kwargs):
                return func(self_weak(), *args, **kwargs)

            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_func

    return decorator
