from functools import wraps
from time import perf_counter, sleep
from typing import Any, Callable



def timing(func: Callable[..., Any]) -> Callable[..., Any]:

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = perf_counter()
        

        try:
            return func(*args, **kwargs)

        finally:
            end_time = perf_counter()
            elapsed_time = end_time - start_time

            print(f"{func.__name__} took {elapsed_time:.4f} seconds")

    return wrapper


def retry(
    times: int = 3,
    delay: float = 1,
    exceptions: tuple[type[Exception], ...] = (TimeoutError, ConnectionError),
) -> Callable[..., Any]:

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)

                except exceptions:
                    if attempt == times - 1:
                        raise

                    sleep(delay)

        return wrapper

    return decorator