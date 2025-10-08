from design.comunication.bus_adapter import BusAdapter
from design.dto.dto import SubmitDraftForReviewCommand
from design.models import ApprovalCenter, ApprovalItem, ReformulatedResearchQuestionIteration, ResearchQuestionHistory, ResearchOwner
from django.db import transaction 

class ResearchQuestionHistoryService:
    def store_question_iteration_on_history(self, iteration: ReformulatedResearchQuestionIteration) -> ReformulatedResearchQuestionIteration:
        iteration.full_clean()
        iteration.save()
        ResearchQuestionHistory.objects.create(
            research_question=iteration.research_question,
            iteration=iteration,
        )
        return iteration

class ApprovalCenterService:
    def publish_draft_to_approval_center(self, iteration: ReformulatedResearchQuestionIteration) -> ApprovalItem:
        assigned_owner = ResearchOwner.objects.first()
        if not assigned_owner:
            raise ValueError("No ResearchOwner available to assign review.")

        center, _ = ApprovalCenter.objects.get_or_create(owner=assigned_owner)
        item = ApprovalItem.objects.create(
            approval_center=center,
            iteration=iteration,
            submitted_by=iteration.researcher,
        )
        BusAdapter().publish_event(
            "research_question.sent_to_owner_for_review",
            {
                "approval_center_id": center.id,
                "approval_item_id": item.id,
                "owner_id": assigned_owner.id,
                "iteration_id": iteration.id,
                "research_question_id": iteration.research_question_id,
                "submitted_by_id": iteration.researcher_id,
                "status": iteration.status,
            }
        )
        return item

class ResearchQuestionSubmissionService:
    def __init__(self):
        self._history = ResearchQuestionHistoryService()
        self._approvals = ApprovalCenterService()

    @transaction.atomic
    def submit_draft_for_review(self, refained_question_cmd: SubmitDraftForReviewCommand) -> int:
        reformulated = ReformulatedResearchQuestionIteration(
            researcher_id=refained_question_cmd.researcher_id,
            research_question_id=refained_question_cmd.research_question_id,
            framework_id=refained_question_cmd.framework_id,
            filled_fields=refained_question_cmd.filled_fields,
            reformulated_research_question=refained_question_cmd.reformulated_text,
            status=refained_question_cmd.status,
            iteration_number=(
                ReformulatedResearchQuestionIteration.objects
                .filter(research_question_id=refained_question_cmd.research_question_id)
                .count() + 1
            ),
        )
        saved_iteration = self._history.store_question_iteration_on_history(reformulated) # aqui la guardo en el historial
        if saved_iteration.status == 'to_review':
            self._approvals.publish_draft_to_approval_center(saved_iteration) # si es to review, la envio a aprobacion
            return 1
        return 0
        