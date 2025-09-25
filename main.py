from diseno.repository.repository import DesignRepository
from diseno.services.design_service import DesignService
from interpretacion.logic.interpretation import InterpretationModule
from seleccion.logic.selection import SelectionModule
from shared.bus.internal_message_bus import InternalMessageBus

if __name__ == "__main__":
    bus = InternalMessageBus()

    # Inicializar módulos
    repo = DesignRepository()
    design_service = DesignService(repo, bus)
    selection_module = SelectionModule(bus)
    interpretation_module = InterpretationModule(bus)

    # Crear una PI de ejemplo
    design_service.create_design("D001", {"pregunta": "¿Cuál es el impacto de las hamburguesas en los niños de 0 a 1 año?"})
