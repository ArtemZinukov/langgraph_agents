from typing import Any

from app.core.exceptions import handle_node_exceptions
from app.core.logging import TicketLoggerAdapter
from app.core.models import SupportState
from app.services.kb_service import search_knowledge_base


@handle_node_exceptions
async def node_search_kb(state: SupportState, t_logger: TicketLoggerAdapter) -> dict[str, Any]:
    t_logger.info("Запрос к базе знаний по извлеченным сущностям...")

    entities = state.get("entities", {})

    docs = await search_knowledge_base(entities)

    t_logger.info(f"Найдено релевантных документов: {len(docs)}")
    return {"documents": docs}
