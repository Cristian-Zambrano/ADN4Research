from unittest.mock import Mock, patch

from django.test import Client

def before_scenario(context, scenario):
    # Creamos un mock y lo adjuntamos al contexto para poder verificarlo luego
    context.client = Client()

    context.mock_notification_patcher = patch(
        'design.services.notification_service.dispatch_notification_for_review'
    )
    context.mock_notification = context.mock_notification_patcher.start()

    # Mock para el feature de validación (Escenario 3: Approve)
    context.mock_notification_approval_patcher = patch(
        'design.services.research_question_services.notification_service.dispatch_notification_for_approval'
    )
    context.mock_notification_approval = context.mock_notification_approval_patcher.start()
    
    # Mock para el feature de validación (Escenario 4: Reject)
    context.mock_notification_rejection_patcher = patch(
        'design.services.research_question_services.notification_service.dispatch_notification_for_rejection'
    )
    context.mock_notification_rejection = context.mock_notification_rejection_patcher.start()
    


def after_scenario(context, scenario):
    # Detenemos el parche para no afectar otras pruebas
    context.mock_notification_patcher.stop()
    context.mock_notification_approval_patcher.stop()
    context.mock_notification_rejection_patcher.stop()