from unittest.mock import patch
from behave import given, when, then, step
from datetime import datetime
from django.contrib.auth.models import User

from design.comunication import events as bus_events
from design.dto.dto import SubmitDraftForReviewCommand
from design.models import ApprovalCenter, ApprovalItem, Framework, ReformulatedResearchQuestionIteration, ResearchOwner, ResearchQuestion, ResearchQuestionHistory, Researcher
from design.services.services import ResearchQuestionSubmissionService


def before_all(context):
    frameworks = [
        ("PICO", {"Population": "aa", "Intervention": "aa", "Comparison": "aaa", "Outcome": "aaa"}),
        ("PCC", {"Population": "Population", "Concept": "Concept", "Context": "Context"}),
        ("PEO", {"Population": "Population", "Exposure": "Exposure", "Outcome": "Outcome"}),
    ]

    for name, fields in frameworks:
        Framework.objects.get_or_create(name=name, defaults={"fields": fields})


def before_scenario(context, scenario):
    context.published_events = []

    # Normaliza y captura eventos del bus interno
    def _capture_internal(event_type, data, source_module):
        context.published_events.append({
            "event": event_type,
            "payload": data,
            "source": source_module,
        })

    # Captura eventos si alguien usa BusAdapter (opcional)
    def _capture_adapter(event_name, payload, **kwargs):
        context.published_events.append({
            "event": event_name,
            "payload": payload,
            "source": "adapter",
        })

    context._bus_internal_patcher = patch(
        'shared.internal_message_bus.MessageBus.publish_event',
        side_effect=_capture_internal
    )
    context._bus_internal_patcher.start()

    context._bus_adapter_patcher = patch(
        'design.comunication.bus_adapter.BusAdapter.publish_event',
        side_effect=_capture_adapter
    )
    context._bus_adapter_patcher.start()


def after_scenario(context, scenario):
    if hasattr(context, '_bus_patcher'):
        context._bus_patcher.stop()

@given('I have the research question "{question}"')
def step_given_research_question(context, question):
    context.researcher = Researcher.objects.create(
        user=User.objects.create_user(username='test_researcher'),
        name='Test Researcher'
    )
    context.research_question = ResearchQuestion.objects.create(
        original_text=question,
        created_by=context.researcher,
        created_at=datetime.now(),
    )
    assert context.research_question.original_text == question
    assert context.research_question.id is not None
  
@step('I have completed all the "{fields}" required by the "{framework}"')
def step_when_complete_framework_fields(context, framework, fields):
    before_all(context)
    framework_obj = Framework.objects.get(name=framework)
    required_fields = list(framework_obj.fields.keys())
    provided_fields = [f.strip() for f in fields.split(',')]
    missing_fields = [f for f in required_fields if f not in provided_fields]
    extra_fields = [f for f in provided_fields if f not in required_fields]
    context.framework_obj = framework_obj
    context.required_fields = required_fields
    context.provided_fields = provided_fields
    context.missing_fields = missing_fields
    context.extra_fields = extra_fields
    assert not missing_fields
    assert not extra_fields

@step('I have provided the reformulated question text')
def step_and_write_reformulated_question(context):
     # Simulo la entrada manual del researcher
    context.reformulated_research_question = (
        "¿Cómo influye la integración de tecnología educativa (intervención)"
        "en estudiantes de instituciones educativas (población) comparado con métodos tradicionales"
        "(comparación) para mejorar la efectividad del aprendizaje (resultado)?"
    )
    pass #Lo dejo pasar porque se valida en el envio

@when('I send the draft to the research owner for review')
def step_and_send_draft_for_review(context):
    context.research_owner = ResearchOwner.objects.create(
        user=User.objects.create_user(username='test_owner'),
        name='Test Owner'
    )
    submition_service = ResearchQuestionSubmissionService()
    refained_question_cmd = SubmitDraftForReviewCommand(
        researcher_id=context.researcher.id,
        research_question_id=context.research_question.id,
        framework_id=context.framework_obj.id,
        filled_fields={f: f"{f}-example" for f in context.provided_fields},
        reformulated_text=context.reformulated_research_question,
        status='to_review',
    )
    context.submission_result = submition_service.submit_draft_for_review(refained_question_cmd)
    assert context.submission_result == 1
    # Capturo la iteración creada para validarla en el Then

@then('a reformulated version of the question should be generated and stored in the research question history including:')
def step_then_reformulated_version_generated(context):
    context.iteration = (
        ReformulatedResearchQuestionIteration.objects
        .filter(
            researcher=context.researcher,
            research_question=context.research_question,
            status='to_review'
        )
        .order_by('-created_at')
        .first()
    )
    assert context.iteration is not None
    # Validaciones básicas de los elementos visibles
    assert context.iteration.researcher.id == context.researcher.id
    assert context.iteration.research_question.id == context.research_question.id
    assert context.iteration.framework.id == context.framework_obj.id
    assert set(context.iteration.filled_fields.keys()) == set(context.provided_fields)
    assert context.iteration.reformulated_research_question == context.reformulated_research_question
    assert context.iteration.status == 'to_review'
    assert context.iteration.iteration_number >= 1
    assert context.iteration.created_at is not None

@step('the system should notify the owner about the iteration to approve')
def step_then_system_sends_notify_for_review(context):
    center = ApprovalCenter.objects.get(owner=context.research_owner)
    item = ApprovalItem.objects.filter(
        approval_center=center,
        iteration=context.iteration
    ).first()
    assert item is not None, "Approval item not created for iteration/owner"
    expected_event = "research_question.sent_to_owner_for_review"

    events = getattr(context, 'published_events', None)
    if not events:
        from shared.internal_message_bus import get_message_bus
        events = get_message_bus().get_published_events()

    assert events, "No events were published"
    match = next(
        (e for e in events
         if e.get("event") == expected_event
         and e.get("payload", {}).get("approval_item_id") == item.id
         and e.get("payload", {}).get("owner_id") == context.research_owner.id
         and e.get("payload", {}).get("iteration_id") == context.iteration.id),
        None
    )
    assert match is not None, "Notification event not published or payload mismatch"

@step('I choose a framework "{framework}"')
def step_and_choose_framework(context, framework):
    context.selected_framework = Framework.objects.get(name=framework)
    assert context.selected_framework is not None

@when('I have completed "{partially_completed_fields}" of the "{framework}"')
def step_when_partially_complete_framework_fields(context, partially_completed_fields, framework):
    before_all(context)
    framework_obj = Framework.objects.get(name=framework)
    required_fields = list(framework_obj.fields.keys())
    provided_fields = [f.strip() for f in partially_completed_fields.split(',')]
    missing_fields = [f for f in required_fields if f not in provided_fields]
    extra_fields = [f for f in provided_fields if f not in required_fields]
    context.framework_obj = framework_obj
    context.required_fields = required_fields
    context.provided_fields = provided_fields
    context.missing_fields = missing_fields
    context.extra_fields = extra_fields
    assert missing_fields  # Deben faltar campos
    assert not extra_fields

@step('And I have not yet completed all required information')
def step_and_not_complete_all_required_information(context):
    context.reformulated_research_question = ""
    
    pass  # Lo dejo pasar porque se valida en el envio

