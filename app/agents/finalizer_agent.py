from typing import Any

from app.core.config import settings
from app.core.logging import TicketLoggerAdapter, get_logger
from app.core.models import SupportState

logger = get_logger()


async def node_escalate(state: SupportState) -> dict[str, Any]:
    """Узел эскалации при обнаружении жалоб."""
    t_logger = TicketLoggerAdapter(logger, {"ticket_id": state.get("ticket_id", "SYS")})
    t_logger.warning("Бизнес-маршрут: Обнаружена жалоба. Эскалация на оператора.")
    return {
        "escalated": True,
        "escalation_reason": "complaint",
        "final_response": "Приносим извинения за доставленные неудобства. Ваше обращение передано живому оператору.",
    }


async def node_finalize(state: SupportState) -> dict[str, Any]:
    """Узел успешного завершения пайплайна."""
    t_logger = TicketLoggerAdapter(logger, {"ticket_id": state.get("ticket_id", "SYS")})

    if state.get("qa_score", 0) < settings.QA_THRESHOLD:
        t_logger.error("Лимит итераций доработки исчерпан! Ответ отправлен клиенту 'как есть' с низким QA-рангом.")
    else:
        t_logger.info("Ответ успешно утвержден QA и готов к отправке.")

    return {"escalated": False, "escalation_reason": "", "final_response": state.get("draft", "")}


async def node_fallback(state: SupportState) -> dict[str, Any]:
    """Аварийный узел на случай падения инфраструктуры."""
    t_logger = TicketLoggerAdapter(logger, {"ticket_id": state.get("ticket_id", "SYS")})
    t_logger.error(f"Аварийный маршрут! Пайплайн прерван из-за ошибки: {state.get('error')}")
    return {
        "escalated": True,
        "escalation_reason": f"technical_error: {state.get('error')}",
        "final_response": "Извините, сейчас у нас технические неполадки. Ваша заявка сохранена и передана инженеру.",
    }
