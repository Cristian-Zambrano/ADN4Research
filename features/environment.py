from unittest.mock import Mock, patch

from django.test import Client

def before_scenario(context, scenario):
    # Creamos un mock y lo adjuntamos al contexto para poder verificarlo luego
    context.client = Client()
    context.mock_notification_patcher = patch('design.services.notification_service.dispatch_notification_for_review')
    context.mock_notification = context.mock_notification_patcher.start()

def after_scenario(context, scenario):
    # Detenemos el parche para no afectar otras pruebas
    context.mock_notification_patcher.stop()