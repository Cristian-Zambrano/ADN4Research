from shared.bus.internal_message_bus import InternalMessageBus

class BusAdapter:
    bus = InternalMessageBus()

    def publish_event(self, event_name, payload):
        self.bus.publish(event_name, payload)

    def subscribe_event(self, event_name, callback):
        self.bus.subscribe(event_name, callback)