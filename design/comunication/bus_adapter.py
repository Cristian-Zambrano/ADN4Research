from shared.internal_message_bus import get_message_bus
from typing import Dict, Any


class BusAdapter:
    """Design module bus adapter - only handles design-specific events"""
    def __init__(self):
        self._bus = get_message_bus()
        self._module_name = "design"
    
    def publish_event(self, event_type: str, payload: Dict[str, Any]):
        """Publish event through the central message bus"""
        self._bus.publish_event(
            event_type=event_type,
            data=payload,
            source_module=self._module_name
        )
    
    def subscribe_to_event(self, event_type: str, handler):
        """Subscribe to events from other modules"""
        self._bus.subscribe_to_event(event_type, handler)

_bus_adapter = BusAdapter()
def get_bus_adapter() -> BusAdapter:
    return _bus_adapter