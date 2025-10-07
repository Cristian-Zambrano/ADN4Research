from design.bus_adapter.bus_adapter import BusAdapter
from design.models.models import ReformulatedResearchQuestionIteration
from design.bus_adapter import events as bus_events


class ResearchQuestionSubmissionService:
    def submit_draft_for_review(self, command):
        reformulated_question = ReformulatedResearchQuestionIteration(
            researcher_id=command.researcher_id,
            created_by_id=command.researcher_id,  # ensure required field
            research_question_id=command.research_question_id,
            framework_id=command.framework_id,
            filled_fields=command.filled_fields,
            reformulated_research_question=command.reformulated_text,
            status='to_review',
            iteration_number=(
                ReformulatedResearchQuestionIteration.objects
                .filter(research_question_id=command.research_question_id)
                .count() + 1
            )
        )
        ResearchQuestionHistoryService().store_question_iteration_on_history(reformulated_question)
        return reformulated_question

class ResearchQuestionHistoryService:
    # Contrato de eventos publicados por el módulo de diseño
    RQ_DRAFT_TO_REVIEW_CREATED = "rq.draft.to_review.created"
    RQ_DRAFT_INCOMPLETE_SAVED = "rq.draft.incomplete.saved"
    def store_question_iteration_on_history(self, reformulated_question):
        reformulated_question.save()
        event_by_status = {
            'to_review': bus_events.RQ_DRAFT_TO_REVIEW_CREATED,
            'incomplete_draft': bus_events.RQ_DRAFT_INCOMPLETE_SAVED,
        }
        event_name = event_by_status.get(getattr(reformulated_question, 'status', None))
        if event_name:
            payload = {
                "refinement_iteration_id": reformulated_question.id,
                "iteration_number": getattr(reformulated_question, "iteration_number", None),
                "research_question_id": reformulated_question.research_question_id,
                "researcher_id": reformulated_question.researcher_id,
                "framework": getattr(reformulated_question.framework, "name", None),
                "filled_fields": getattr(reformulated_question, "filled_fields", None),
                "reformulated_research_question": getattr(reformulated_question, "reformulated_research_question", None),
                "status": reformulated_question.status,
                "created_at": (
                    reformulated_question.created_at.isoformat()
                    if getattr(reformulated_question, "created_at", None) else None
                ),
            }
            BusAdapter().publish_event(event_name, payload)

        return reformulated_question

    def exist_question_on_history(self, question_id):
        return ReformulatedResearchQuestionIteration.objects.filter(research_question_id=question_id).exists()
        