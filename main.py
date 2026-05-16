import asyncio
import uuid
from typing import Any

from app.core.logging import TicketLoggerAdapter, get_logger
from app.core.models import SupportState
from app.graph.workflow import app_graph

logger = get_logger()


async def process_ticket(ticket_id: str, query: str) -> None:
    """Функция оркестрации одного конкретного обращения."""
    t_logger = TicketLoggerAdapter(logger, {"ticket_id": ticket_id})
    t_logger.info("--- НАЧАЛО ОБРАБОТКИ ТИКЕТА ---")

    # Формируем стартовое состояние
    initial_state: SupportState = {
        "ticket_id": ticket_id,
        "query": query,
        "retry_count": 0,
        "entities": {},
        "documents": [],
        "escalated": False,
        "error": None,
    }

    try:
        final_state: Any = await app_graph.ainvoke(initial_state)

        t_logger.info(f"Обработка завершена. Статус эскалации: {final_state.get('escalated')}")
        print(f"\n[Ticket: {ticket_id}]")
        print(f"Пользователь: {query}")
        print(f"Ответ системы: {final_state.get('final_response')}")
        if final_state.get("escalated"):
            print(f"⚠️ Причина эскалации: {final_state.get('escalation_reason')}")
        print("-" * 50)

    except Exception as exc:
        t_logger.critical(f"Критический сбой запуска LangGraph: {exc}", exc_info=True)


async def main() -> None:
    """Главная функция запуска демонстрации сценариев."""
    logger.info("Запуск Мультиагентной Системы Технической Поддержки...")

    # Успешный сценарий
    await process_ticket(
        ticket_id=f"T-{uuid.uuid4().hex[:6].upper()}", query="Как мне сбросить пароль в личном кабинете?"
    )

    # Сценарий с жалобой, где intent - "complaint"
    await process_ticket(
        ticket_id=f"T-{uuid.uuid4().hex[:6].upper()}",
        query="Ужасный сервис! Ваше приложение постоянно вылетает, я буду жаловаться!",
    )

    # Сценарий c доработкой от QA
    await process_ticket(ticket_id=f"T-{uuid.uuid4().hex[:6].upper()}", query="Мне плохо понятно, как обновиться.")

    # Сценарий технического сбоя
    await process_ticket(
        ticket_id=f"T-{uuid.uuid4().hex[:6].upper()}", query="Что делать, если выскакивает ошибка 500 при авторизации?"
    )


if __name__ == "__main__":
    asyncio.run(main())
