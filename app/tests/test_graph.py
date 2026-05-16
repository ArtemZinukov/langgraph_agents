from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import ServiceError
from app.core.models import SupportState
from app.graph.workflow import app_graph, route_extraction, route_qa


@pytest.fixture
def base_state() -> SupportState:
    """Фикстура базового состояния для тестов роутеров."""
    return {
        "query": "Тестовый запрос",
        "intent": None,
        "entities": {},
        "documents": [],
        "draft": "",
        "qa_score": 0.0,
        "qa_feedback": "",
        "retry_count": 0,
    }


@pytest.mark.asyncio
@patch("app.agents.intent_agent.extract_intent_llm")
async def test_pipeline_escalation_branch(mock_extract: AsyncMock) -> None:
    """
    ТЗ: Тестирование ветки эскалации.
    Проверяет, что при интенте 'complaint' граф успешно доходит до конца,
    сохраняя интент жалобы.
    """
    mock_extract.return_value = AsyncMock(intent="complaint", entities=[])

    final_state = await app_graph.ainvoke({"query": "Верните деньги, ваш сервис ужасен!"})

    assert final_state["intent"] == "complaint"


def test_route_extraction_complaint(base_state: SupportState) -> None:
    """Дополнительный Unit-тест роутера extraction на жалобу."""
    base_state["intent"] = "complaint"
    assert route_extraction(base_state) == "escalate"


@pytest.mark.asyncio
@patch("app.agents.intent_agent.extract_intent_llm")
@patch("app.agents.knowledge_agent.node_search_kb")
@patch("app.agents.generation_agent.generate_draft_llm")
@patch("app.agents.qa_agent.evaluate_qa_llm")
async def test_pipeline_revision_loop_and_limit(
    mock_evaluate_qa_llm: AsyncMock,
    mock_generate_draft_llm: AsyncMock,
    mock_node_search_kb: AsyncMock,
    mock_extract: AsyncMock,
) -> None:
    """
    ТЗ: Тестирование цикла доработки (включая остановку после исчерпания лимита).
    Проверяет, что при плохой оценке QA граф возвращается к генерации черновика,
    но останавливается ровно после MAX_REVISION_ITERATIONS (2).
    """

    mock_extract.return_value = AsyncMock(intent="question", entities=[])
    mock_node_search_kb.return_value = {"documents": ["Инструкция..."]}

    mock_generate_draft_llm.return_value = "Черновик ответа"

    mock_evaluate_qa_llm.return_value = AsyncMock(score=0.4, feedback="Плохо")

    final_state = await app_graph.ainvoke({"query": "Как настроить систему?", "retry_count": 0})

    assert final_state["retry_count"] == 2
    assert final_state["qa_score"] == 0.4
    assert "draft" in final_state


def test_route_qa_loop_and_exit(base_state: SupportState) -> None:
    """Unit-тест роутера QA на проверку условий перехода."""
    base_state["qa_score"] = 0.8
    assert route_qa(base_state) == "finalize"

    base_state["qa_score"] = 0.3
    base_state["retry_count"] = 0
    assert route_qa(base_state) == "draft"

    base_state["retry_count"] = 2
    assert route_qa(base_state) == "finalize"


@pytest.mark.asyncio
@patch("app.agents.intent_agent.extract_intent_llm")
async def test_pipeline_error_handling_fallback(mock_extract: AsyncMock) -> None:
    """
    ТЗ: Тестирование обработки ошибок.
    Проверяет, что декоратор @handle_node_exceptions перехватывает ServiceError,
    добавляет ключ 'error' в стейт, и роутер уводит граф в узел 'fallback'.
    """
    mock_extract.side_effect = ServiceError("Ошибка подключения к LLM-провайдеру")

    final_state = await app_graph.ainvoke({"query": "Сломает ли это систему?"})

    assert "error" in final_state
    assert "Ошибка подключения к LLM-провайдеру" in final_state["error"]


def test_route_extraction_on_error(base_state: SupportState) -> None:
    """Unit-тест роутера extraction: при наличии ошибки всегда уходим в fallback."""
    base_state["error"] = "Критический сбой"
    assert route_extraction(base_state) == "fallback"
