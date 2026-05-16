import time
from functools import wraps
from typing import Any, Callable, Coroutine, TypeVar

from app.core.logging import get_logger

logger = get_logger()

R = TypeVar("R")


def log_latency(
    operation_name: str,
) -> Callable[[Callable[..., Coroutine[Any, Any, R]]], Callable[..., Coroutine[Any, Any, R]]]:
    """
    Декоратор-фабрика для автоматического замера latency асинхронных вызовов.
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, R]]) -> Callable[..., Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            t_logger = kwargs.get("t_logger", logger)

            t_logger.debug(f"Отправка запроса ({operation_name})...")
            start_time = time.perf_counter()

            result = await func(*args, **kwargs)

            latency = time.perf_counter() - start_time
            t_logger.info(f"{operation_name} успешно завершена за {latency:.4f}s.")
            return result

        return wrapper

    return decorator
