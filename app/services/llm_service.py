import asyncio

from app.core.exceptions import ServiceError
from app.core.models import ExtractionResult, QAResult


async def extract_intent_llm(query: str) -> ExtractionResult:
    """Имитация вызова Structured Output от LLM."""
    await asyncio.sleep(0.1)

    if "ошибка 500" in query.lower():
        raise ServiceError("OpenAI API Gateway Timeout (Status 500)")

    if "жалоба" in query.lower() or "ужасно" in query.lower():
        return ExtractionResult(intent="complaint", entities={"sentiment": "negative"})

    return ExtractionResult(intent="question", entities={"topic": "general"})


async def generate_draft_llm(query: str, docs: list[str], feedback: str) -> str:
    """Имитация генерации ответа модели на основе контекста БЗ и критики."""
    await asyncio.sleep(0.1)
    if feedback:
        return f"Исправленный ответ с учетом замечания '{feedback}': Для решения вашей проблемы используйте {docs[0]}."

    if "плохо" in query.lower():
        return "Ответ: Разбирайтесь сами, вся информация есть на сайте."

    doc_info = docs[0] if docs else "информации в базе знаний не найдено."
    return f"Ответ: Согласно базе знаний компании, {doc_info}"


async def evaluate_qa_llm(draft: str) -> QAResult:
    """Имитация работы QA-агента (Критика)."""
    await asyncio.sleep(0.1)
    if "Разбирайтесь сами" in draft:
        return QAResult(score=0.3, feedback="Тон ответа абсолютно невежлив и груб.")
    return QAResult(score=0.9, feedback="Ответ вежливый, точный и релевантный.")
