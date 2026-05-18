from langgraph.graph import END, StateGraph

from app.agents.finalizer_agent import node_escalate, node_fallback, node_finalize
from app.agents.generation_agent import node_draft
from app.agents.intent_agent import node_extract
from app.agents.knowledge_agent import node_search_kb
from app.agents.qa_agent import node_qa
from app.core.config import settings
from app.core.models import SupportState, TicketIntent


def route_extraction(state: SupportState) -> str:
    if state.get("error"):
        return "fallback"

    match state.get("intent"):
        case TicketIntent.COMPLAINT:
            return "escalate"
        case TicketIntent.QUESTION | TicketIntent.ASSISTANCE:
            return "search_kb"
        case _:
            return "fallback"


def route_qa(state: SupportState) -> str:
    if state.get("error"):
        return "fallback"
    if state.get("qa_score", 0) >= settings.QA_THRESHOLD:
        return "finalize"
    if state.get("retry_count", 0) < settings.MAX_REVISION_ITERATIONS:
        return "draft"
    return "finalize"


def build_graph() -> StateGraph:
    workflow = StateGraph(SupportState)

    workflow.add_node("extract", node_extract)
    workflow.add_node("search_kb", node_search_kb)
    workflow.add_node("draft", node_draft)
    workflow.add_node("qa", node_qa)
    workflow.add_node("escalate", node_escalate)
    workflow.add_node("finalize", node_finalize)
    workflow.add_node("fallback", node_fallback)

    # Настраиваем связи
    workflow.set_entry_point("extract")

    workflow.add_conditional_edges("extract", route_extraction)
    workflow.add_edge("search_kb", "draft")

    # Защитная проверка: если на этапе генерации черновика произошел сбой
    workflow.add_conditional_edges("draft", lambda s: "fallback" if s.get("error") else "qa")

    workflow.add_conditional_edges("qa", route_qa)

    # Терминальные узлы ведут к выходу из графа
    workflow.add_edge("escalate", END)
    workflow.add_edge("finalize", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()


app_graph = build_graph()
