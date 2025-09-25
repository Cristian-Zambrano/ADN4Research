class DesignService:
    def __init__(self, repository, bus):
        self.repository = repository
        self.bus = bus

    def create_design(self, design_id, data):
        self.repository.save(design_id, data)
        print(f"[DISEÑO] Diseño creado con ID: {design_id}")
        # Publica evento
        self.bus.publish("design.created", {"id": design_id, "data": data})