from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class ExtractionResult(BaseModel):
    """Схема структурированного ответа от Intent Agent."""

    intent: Literal["question", "complaint", "assistance"] = Field(
        description="Основное намерение пользователя в обращении"
    )

    entities: Annotated[
        dict[str, Any],
        Field(default_factory=dict, description="Извлеченные именованные сущности (продукт, версия, симптомы и т.д.)"),
    ]


class QAResult(BaseModel):
    """Схема критической оценки от QA Agent."""

    score: float = Field(ge=0.0, le=1.0, description="Числовая оценка качества ответа от 0.0 до 1.0")
    feedback: str = Field(description="Замечания, критика и рекомендации по исправлению текста ответа")


class SupportState(TypedDict, total=False):
    """
    Глобальное состояние (State) LangGraph, передающееся между агентами.
    Использует total=False, что позволяет узлам обновлять только
    часть полей (partial updates) через обычный возврат словарей.
    """

    # Входные данные тикета
    ticket_id: str
    query: str

    # Контекст, наполняемый агентами в процессе работы
    intent: Optional[Literal["question", "complaint", "assistance"]]
    entities: Dict[str, Any]
    documents: List[str]
    draft: str

    # Метрики контроля качества и итерации
    qa_score: float
    qa_feedback: str
    retry_count: int

    # Выходные (финальные) данные системы
    final_response: str
    escalated: bool
    escalation_reason: str

    # Инфраструктурное поле для отслеживания сбоев
    error: Optional[str]
