from typing import Any

from app.core.exceptions import handle_node_exceptions
from app.core.logging import TicketLoggerAdapter
from app.core.models import SupportState
from app.services.llm_service import generate_draft_llm


@handle_node_exceptions
async def node_draft(state: SupportState, t_logger: TicketLoggerAdapter) -> dict[str, Any]:
    current_retry = state.get("retry_count", 0)
    t_logger.info(f"Запуск генерации черновика ответа (Итерация ревизии: {current_retry})")

    draft = await generate_draft_llm(
        query=state.get("query", ""),
        docs=state.get("documents", []),
        feedback=state.get("qa_feedback", ""),
        t_logger=t_logger,
    )
    return {"draft": draft}
