class SelectionModule:
    def __init__(self, bus):
        # Se suscribe al evento
        bus.subscribe("design.created", self.on_design_created)

    def on_design_created(self, event):
        print(f"[SELECCIÓN] Preparando búsqueda para diseño {event['id']}")
