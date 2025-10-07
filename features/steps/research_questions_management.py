from unittest.mock import patch
from behave import given, when, then, step
from datetime import datetime
from django.contrib.auth.models import User

from design.bus_adapter import events as bus_events
from design.dto.dto import SubmitDraftForReviewCommand
from design.models.models import Framework, ReformulatedResearchQuestionIteration, ResearchQuestion, Researcher
from design.services.services import ResearchQuestionHistoryService, ResearchQuestionSubmissionService

def before_scenario(context, scenario):
    # Captura de eventos publicados por el BusAdapter
    context.published_events = []

    def _capture(event_name, payload, **kwargs):
        context.published_events.append({"event": event_name, "payload": payload, **kwargs})
        # devolver algo similar a un envelope si lo necesitas en asserts adicionales
        return {"event": event_name, "payload": payload, **kwargs}

    context._bus_patcher = patch(
        'design.bus_adapter.bus_adapter.BusAdapter.publish_event',
        side_effect=_capture
    )
    context._bus_patcher.start()
    Framework.objects.get_or_create(name="PICO", defaults={
        "fields": {"P": "Population", "I": "Intervention", "C": "Comparison", "O": "Outcome"}
    })
    Framework.objects.get_or_create(name="PCC", defaults={
        # use distinct codes to avoid duplicate keys; names drive validation
        "fields": {"P": "Population", "C": "Concept", "X": "Context"}
    })
    Framework.objects.get_or_create(name="PEO", defaults={
        "fields": {"P": "Population", "E": "Exposure", "O": "Outcome"}
    })

def after_scenario(context, scenario):
    if hasattr(context, '_bus_patcher'):
        context._bus_patcher.stop()

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

@when('I complete all the "{fields}" required by the "{framework}"')
def step_when_complete_framework_fields(context, framework, fields):
    framework_obj = Framework.objects.get(name=framework)
    required_fields = list(framework_obj.fields.keys())
    provided_fields = [f.strip().split()[0][0].upper() for f in fields.split(',')]
    missing_fields = [f for f in required_fields if f not in provided_fields]
    extra_fields = [f for f in provided_fields if f not in required_fields]
    
    context.framework_obj = framework_obj
    context.required_fields = required_fields
    context.provided_fields = provided_fields
    context.missing_fields = missing_fields
    context.extra_fields = extra_fields
    
    assert not missing_fields, (
        f"Missing required fields for {framework}: {', '.join(missing_fields)}"
    )
    assert not extra_fields, (
        f"Unexpected fields provided for {framework}: {', '.join(extra_fields)}"
    )
    
@step('I provide the reformulated question text ')
def step_and_write_reformulated_question(context):
     # Simulo la entrada manual del researcher
    context.reformulated_research_question = (
        "¿Cómo influye la integración de tecnología educativa (intervención)"
        "en estudiantes de instituciones educativas (población) comparado con métodos tradicionales"
        "(comparación) para mejorar la efectividad del aprendizaje (resultado)?"
    )
    pass #Lo dejo pasar porque se valida en el paso del then

@step('I send the draft to the research owner for review')
def step_and_send_draft_for_review(context):
    submition_service = ResearchQuestionSubmissionService()
    cmd = SubmitDraftForReviewCommand(
        researcher_id=context.researcher.id,
        research_question_id=context.research_question.id,
        framework_id=context.framework_obj.id,
        filled_fields={f: f"{f}-example" for f in context.provided_fields},
        reformulated_text=context.reformulated_research_question,
    )
    context.reformulated_research_question = submition_service.submit_draft_for_review(cmd)
    
@then('a reformulated version of the question should be stored in the research question history including:')
def step_then_reformulated_version_generated(context):
    assert ReformulatedResearchQuestionIteration.objects.filter(
        id=context.reformulated_research_question.id,
        research_question_id=context.research_question.id,
        status='to_review',
    ).exists()

@step('the draft should be published on the approval center')
def step_then_system_sends_draft_for_review(context):
    # No publicar desde el step; solo verificar que el servicio lo publicó
    assert any(
        e["event"] == bus_events.RQ_DRAFT_TO_REVIEW_CREATED
        and e["payload"]["refinement_iteration_id"] == context.reformulated_research_question.id
        and e["payload"]["research_question_id"] == context.research_question.id
        and e["payload"]["researcher_id"] == context.researcher.id
    for e in context.published_events), "Expected event RQ_DRAFT_TO_REVIEW_CREATED was not published"

    