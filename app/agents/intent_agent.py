from typing import Any

from app.core.exceptions import handle_node_exceptions
from app.core.logging import TicketLoggerAdapter
from app.core.models import SupportState
from app.services.llm_service import extract_intent_llm


@handle_node_exceptions
async def node_extract(state: SupportState, t_logger: TicketLoggerAdapter) -> dict[str, Any]:
    t_logger.info(f"Анализ входящего обращения: '{state.get('query')}'")

    result = await extract_intent_llm(state.get("query", ""), t_logger=t_logger)

    t_logger.info(f"Успешно извлечено намерение: {result.intent}")

    return {"intent": result.intent, "entities": result.entities}
