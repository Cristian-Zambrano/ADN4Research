import json
from behave import given, when, then, step
from django.contrib.auth.models import User
from rest_framework import status
from design.models import ResearchQuestion, ResearchQuestionVersion, Task
from projects.models import Project

@given('I have an assigned task to propose research questions for the current project')
def step_impl(context):
    # 1. Crear usuarios y proyecto
    context.researcher = User.objects.create_user(username='researcher', password='password', email='researcher@test.com')
    context.owner = User.objects.create_user(username='owner', password='password', email='owner@test.com')
    context.project = Project.objects.create(name='Test Project', owner=context.owner)
    # 2. Establecer la membresía del investigador
    context.project.add_member(context.researcher, role='researcher')
    context.project.add_member(context.owner, role='owner')
    # 3. Crear la tarea de investigación en diseño
    context.task = Task.objects.create(
        project=context.project,
        title='Propose Research Questions',
        description='Task to propose research questions for the project.',
        created_by=context.owner,
        assigned_to=context.researcher
    )
    context.question = ResearchQuestion.objects.create(
        project=context.project,
        created_by=context.researcher,
    )
    # 4. Iniciar sesión con el cliente de prueba
    context.client.login(username='researcher', password='password')
  
@when('I submit the draft question for review with the following data')
def step_impl(context):
    payload = json.loads(context.text)
    context.payload = payload
    
    url = f'/api/v1/design/questions/{context.question.id}/submit/'
    context.response = context.client.post(
        url,
        data=json.dumps(context.payload),
        content_type='application/json'
    )

@then('a new version of the question should be created with its status set to "{question_status}"')
def step_impl(context, question_status):
    assert context.response.status_code == status.HTTP_201_CREATED
    context.question.refresh_from_db()
    context.new_version = context.question.versions.latest('submitted_at')
    assert context.new_version.status == question_status.upper()

@step('the new version data must match the submitted data')
def step_impl(context):
    payload = context.payload
    version = context.new_version

    # Perform detailed assertions
    assert version.researcher == context.researcher
    assert version.framework == payload['framework'].upper()
    assert version.reformulated_text == payload['reformulated_text']
    assert version.framework_fields == payload['fields']
    assert version.submitted_at is not None


@step('a notification request should be dispatched to the communication module')
def step_impl(context):
    context.mock_notification.assert_called_once()
# Segundo escenario
@given('I am working on a research question for the "{framework}" framework')
def step_impl(context, framework):
    # 1. Configuración mínima: usuario, proyecto y pregunta contenedora.
    context.researcher = User.objects.create_user(username='researcher', password='password')
    context.owner = User.objects.create_user(username='owner', password='password')
    context.project = Project.objects.create(name='Autosave Project', owner=context.owner)
    context.question = ResearchQuestion.objects.create(
        project=context.project,
        created_by=context.researcher
    )
    
    # 2. Almacenar el framework para usarlo en el 'When'
    context.framework = framework
    
    # 3. Autenticar al cliente para la prueba de API
    context.client.login(username='researcher', password='password')

@when('the system receives a request to save a draft with the following data')
def step_impl(context):
    payload_partial = json.loads(context.text)
    # 2. Construir el payload completo, añadiendo el framework del 'Given'
    context.payload = {
        "framework": context.framework,
        "fields": payload_partial.get("fields", {}),
        "reformulated_text": payload_partial.get("reformulated_text", "")
    }
    # 3. Definir el endpoint para guardar borradores (se asume PUT para idempotencia)
    url = f'/api/v1/design/questions/{context.question.id}/draft/'
    # 4. Realizar la petición a la API
    context.response = context.client.put(
        url,
        data=json.dumps(context.payload),
        content_type='application/json'
    )

@then('a research question version must exist with status "{question_status}"')
def step_impl(context, question_status):
    # 1. Verificar que la API respondió exitosamente (200 OK para una actualización/creación)
    assert context.response.status_code == status.HTTP_200_OK
    # 2. Verificar que el objeto existe en la base de datos con el estado correcto
    try:
        draft_version = ResearchQuestionVersion.objects.get(
            question=context.question,
            researcher=context.researcher,
            status=question_status.upper()
        )
        context.draft_version = draft_version  
    except ResearchQuestionVersion.DoesNotExist:
        assert False, f"No ResearchQuestionVersion with status '{question_status.upper()}' was found."
    except ResearchQuestionVersion.MultipleObjectsReturned:
        assert False, "Found multiple DRAFT versions for the same question and user. The logic should be update-or-create."
    

@step('its data must match the submitted draft data')
def step_impl(context):
    # 1. Recuperar el payload enviado y la versión guardada desde el contexto
    payload = context.payload
    version = context.draft_version
    # 2. Realizar aserciones detalladas para garantizar la integridad de los datos
    assert version.framework == payload['framework'].upper()
    assert version.framework_fields == payload['fields']
    assert version.reformulated_text == payload['reformulated_text']

@step('no notification for review should be sent')
def step_impl(context):
    context.mock_notification.assert_not_called()