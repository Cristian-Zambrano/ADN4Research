class InternalMessageBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_name, callback):
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        self.subscribers[event_name].append(callback)

    def publish(self, event_name, payload):
        print(f"[BUS] Publicando evento: {event_name} con payload: {payload}")
        for callback in self.subscribers.get(event_name, []):
            callback(payload)