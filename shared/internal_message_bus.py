import logging
from typing import Dict, List, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Message:
    message_id: str
    timestamp: datetime
    source_module: str
    event_type: str
    data: Dict[str, Any]

class MessageHandler(ABC):
    @abstractmethod
    def handle(self, message: Message) -> Any:
        ...
        # ...existing code...

class MessageBus:
    def __init__(self):
        self._event_handlers: Dict[str, List[MessageHandler]] = {}
        self._published_events: List[Dict[str, Any]] = []  # buffer for tests

    def subscribe_to_event(self, event_type: str, handler: MessageHandler):
        self._event_handlers.setdefault(event_type, []).append(handler)

    def publish_event(self, event_type: str, data: Dict[str, Any], source_module: str):
        # Store event for tests
        self._published_events.append({
            "event": event_type,
            "payload": data,
            "source": source_module,
        })
        logger.info("Publishing event: %s from %s", event_type, source_module)
        # Invoke handlers (if any)
        for handler in self._event_handlers.get(event_type, []):
            try:
                handler.handle(Message(
                    message_id="",
                    timestamp=datetime.utcnow(),
                    source_module=source_module,
                    event_type=event_type,
                    data=data,
                ))
            except Exception:
                logger.exception("Handler failed for event: %s", event_type)

    def get_published_events(self) -> List[Dict[str, Any]]:
        # Return the live list (tests can read it)
        return self._published_events

    def clear_published_events(self):
        self._published_events.clear()

_message_bus = MessageBus()

def get_message_bus() -> MessageBus:
    return _message_bus