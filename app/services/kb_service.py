import asyncio
from typing import Any


async def search_knowledge_base(entities: dict[str, Any]) -> list[str]:
    """Имитация поиска по векторной базе знаний."""
    await asyncio.sleep(0.1)
    return [
        "Статья №103: Для сброса пароля перейдите в личный кабинет и нажмите 'Забыли пароль'.",
        "Статья №104: Инструкция по обновлению мобильного приложения.",
    ]
