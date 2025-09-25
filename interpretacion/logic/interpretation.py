class InterpretationModule:
    def __init__(self, bus):
        bus.subscribe("design.created", self.on_design_created) # Se suscribe al evento

    def on_design_created(self, event):
        # Aqui se le dice que hacer cuando se recibe el evento
        print(f"[INTERPRETACIÓN] Notificado: diseño {event['id']} creado.")