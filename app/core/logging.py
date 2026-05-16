import logging
from typing import Any, MutableMapping


def get_logger(name: str = "MAS_Support") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - Ticket: %(ticket_id)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class TicketLoggerAdapter(logging.LoggerAdapter[logging.Logger]):
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> tuple[Any, MutableMapping[str, Any]]:
        extra_dict = self.extra if self.extra is not None else {}
        ticket_id = extra_dict.get("ticket_id", "UNKNOWN")

        return msg, {**kwargs, "extra": {"ticket_id": ticket_id}}
