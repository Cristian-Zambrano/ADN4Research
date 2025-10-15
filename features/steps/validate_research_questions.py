
import json
from behave import given, when, then, step
from django.contrib.auth.models import User
from rest_framework import status
from design.models import ResearchQuestion, ResearchQuestionVersion, ValidationHistory
from projects.models import Project

@given('there are research question versions with status "{question_status}" awaiting validation')
def step_impl(context, question_status):
    context.researcher = User.objects.create_user(username='researcher', password='password', email='researcher@test.com')
    context.owner = User.objects.create_user(username='owner', password='password', email='owner@test.com')
    context.project = Project.objects.create(name='Validation Project', owner=context.owner)
    context.project.add_member(context.researcher, role='researcher')
    context.project.add_member(context.owner, role='owner')

    context.question = ResearchQuestion.objects.create(
        project=context.project,
        created_by=context.researcher
    )
    context.version_to_validate = ResearchQuestionVersion.objects.create(
        question=context.question,
        researcher=context.researcher,
        framework='PICO',  # Framework de ejemplo
        framework_fields={
            'Population': 'Adults with diabetes',
            'Intervention': 'Low-carb diet',
            'Comparison': 'Standard diet',
            'Outcome': 'HbA1c levels'
        },
        reformulated_text='What is the effect of a low-carb diet compared to a standard diet on HbA1c levels in adults with diabetes?',
        status=question_status.upper()
    )
    context.expected_status_before_validation = question_status.upper()
    context.client.login(username='owner', password='password')

@when('the owner "{action}" a draft with the justification "{justification}"')
def step_impl(context, justification, action):
    context.action = action.lower()
    url = f'/api/v1/design/questions/{context.question.id}/versions/{context.version_to_validate.id}/{context.action}/'
    payload = {
        "justification": justification
    }
    context.response = context.client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )
    context.justification_sent = justification

@then('the question status should change from "{question_status}" to "{new_status}"')
def step_impl(context, question_status, new_status):
    assert context.response.status_code == status.HTTP_200_OK
    context.version_to_validate.refresh_from_db()
    assert context.version_to_validate.status == new_status.upper()
    assert context.expected_status_before_validation == question_status.upper()

@step('a history record should be created with approver, justification, and date')
def step_impl(context):
    history_record = ValidationHistory.objects.filter(
        version=context.version_to_validate,
        validator=context.owner
    ).latest('validated_at')
    
    assert history_record is not None
    assert history_record.justification == context.justification_sent
    assert history_record.validated_at is not None

@step('all other researchers should receive a notification of the "{new_status}" question')
def step_impl(context, new_status):
    if new_status.upper() == 'APPROVED':
        context.mock_notification_approval.assert_called_once()
        call_kwargs = context.mock_notification_approval.call_args.kwargs
    elif new_status.upper() == 'REJECTED':
        context.mock_notification_rejection.assert_called_once()
        call_kwargs = context.mock_notification_rejection.call_args.kwargs
    assert 'version' in call_kwargs
    assert call_kwargs['version'].id == context.version_to_validate.id
    assert call_kwargs['version'].status == new_status.upper()

# Tercer escenario reutilizando los pasos anteriores
@when('the owner tries to validate an "{question_status}" version again')
def step_impl(context, question_status):
    context.version_to_validate.status = question_status.upper()
    context.version_to_validate.save()
    url = f'/api/v1/design/questions/{context.question.id}/versions/{context.version_to_validate.id}/approve/'
    payload = {
        "justification": "Trying to revalidate"
    }
    context.response = context.client.post(
        url,
        data=json.dumps(payload),
        content_type='application/json'
    )

@then('the system should raise a "{error_type}" indicating revalidation is not allowed')
def step_impl(context, error_type):
    assert context.response.status_code == status.HTTP_400_BAD_REQUEST
    response_data = context.response.json()
    assert 'error' in response_data
    if error_type == "ValidationError":
        assert response_data['error'] == "This version has already been validated and cannot be revalidated."
    elif error_type == "PermissionDenied":
        assert response_data['error'] == "You do not have permission to validate this version."

