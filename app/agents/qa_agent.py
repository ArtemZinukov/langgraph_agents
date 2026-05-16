from typing import Any

from app.core.exceptions import handle_node_exceptions
from app.core.logging import TicketLoggerAdapter
from app.core.models import SupportState
from app.services.llm_service import evaluate_qa_llm


@handle_node_exceptions
async def node_qa(state: SupportState, t_logger: TicketLoggerAdapter) -> dict[str, Any]:
    t_logger.info("Валидация черновика в узле контроля качества (QA)...")

    result = await evaluate_qa_llm(state.get("draft", ""))

    t_logger.info(f"Результат QA проверки -> Оценка: {result.score}")
    return {"qa_score": result.score, "qa_feedback": result.feedback, "retry_count": state.get("retry_count", 0) + 1}
