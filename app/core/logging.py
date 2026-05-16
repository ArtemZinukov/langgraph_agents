import logging
from typing import Any, MutableMapping


class OptionalTicketFormatter(logging.Formatter):
    """Кастомный форматтер. Если у лога нет ticket_id (вызов без адаптера),
    он автоматически подставит 'N/A'."""

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "ticket_id"):
            record.ticket_id = "N/A"
        return super().format(record)


def get_logger(name: str = "MAS_Support") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = OptionalTicketFormatter("%(asctime)s - [%(levelname)s] - Ticket: %(ticket_id)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class TicketLoggerAdapter(logging.LoggerAdapter[logging.Logger]):
    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> tuple[Any, MutableMapping[str, Any]]:
        extra_dict = self.extra if self.extra is not None else {}
        ticket_id = extra_dict.get("ticket_id", "UNKNOWN")

        if "extra" not in kwargs:
            kwargs["extra"] = {}

        kwargs["extra"]["ticket_id"] = ticket_id

        return msg, kwargs
