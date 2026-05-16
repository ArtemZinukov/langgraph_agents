from collections.abc import Awaitable, Callable
from typing import Any

from app.core.logging import TicketLoggerAdapter, get_logger
from app.core.models import SupportState

logger = get_logger()


class ServiceError(Exception):
    """Базовое исключение для внешних сервисов."""

    pass


def handle_node_exceptions(
    func: Callable[[SupportState, TicketLoggerAdapter], Awaitable[dict[str, Any]]],
) -> Callable[[SupportState], Awaitable[dict[str, Any]]]:
    """Декоратор для перехвата исключений в узлах графа."""

    async def wrapper(state: SupportState) -> dict[str, Any]:
        ticket_id = state.get("ticket_id", "SYS") if isinstance(state, dict) else getattr(state, "ticket_id", "SYS")

        t_logger = TicketLoggerAdapter(logger, {"ticket_id": ticket_id})
        try:
            return await func(state, t_logger)
        except Exception as e:
            t_logger.error(f"Критическая ошибка в узле {func.__name__}: {e}")
            return {"error": str(e)}

    return wrapper
