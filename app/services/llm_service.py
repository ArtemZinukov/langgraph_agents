import asyncio

from app.core.decorators import log_latency
from app.core.exceptions import ServiceError
from app.core.logging import TicketLoggerAdapter, get_logger
from app.core.models import ExtractionResult, QAResult

logger = get_logger()


@log_latency("Intent Extraction")
async def extract_intent_llm(query: str, t_logger: TicketLoggerAdapter) -> ExtractionResult:
    """Имитация вызова Structured Output от LLM."""
    await asyncio.sleep(0.1)

    if "ошибка 500" in query.lower():
        t_logger.error("LLM API вернуло статус 500. Инициировано кастомное исключение.")
        raise ServiceError("OpenAI API Gateway Timeout (Status 500)")

    if "жалоб" in query.lower() or "ужасн" in query.lower():
        return ExtractionResult(intent="complaint", entities={"sentiment": "negative"})

    return ExtractionResult(intent="question", entities={"topic": "general"})


@log_latency("Generation")
async def generate_draft_llm(query: str, docs: list[str], feedback: str, t_logger: TicketLoggerAdapter) -> str:
    """Имитация генерации ответа модели на основе контекста БЗ и критики."""
    await asyncio.sleep(0.1)
    if feedback:
        return f"Исправленный ответ с учетом замечания '{feedback}': Для решения вашей проблемы используйте {docs[0]}."

    if "плохо" in query.lower():
        t_logger.warning("Сгенерирован некачественный ответ (триггер 'плохо').")
        return "Разбирайтесь сами, вся информация есть на сайте."

    doc_info = docs[0] if docs else "информации в базе знаний не найдено."
    return f"Согласно базе знаний компании, {doc_info}"


@log_latency("QA-Judge")
async def evaluate_qa_llm(draft: str, t_logger: TicketLoggerAdapter) -> QAResult:
    """Имитация работы QA-агента (Критика)."""
    await asyncio.sleep(0.1)
    if "Разбирайтесь сами" in draft:
        result = QAResult(score=0.3, feedback="Тон ответа абсолютно невежлив и груб.")
        t_logger.warning(f"QA-Judge выставил НИЗКУЮ оценку: {result.score}. Фидбек: {result.feedback}")
        return result
    return QAResult(score=0.9, feedback="Ответ вежливый, точный и релевантный.")
