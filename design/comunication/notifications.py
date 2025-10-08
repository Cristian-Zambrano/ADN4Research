from abc import ABC, abstractmethod
from design.models import ReformulatedResearchQuestionIteration, ResearchOwner


class InternalNotificationStrategy(ABC):
    @abstractmethod
    def notify_research_owner(self, iteration: ReformulatedResearchQuestionIteration) -> None:
        pass


class DirectNotification(InternalNotificationStrategy):
    """Direct synchronous notification within design module"""
    
    def notify_research_owner(self, iteration: ReformulatedResearchQuestionIteration) -> None:
        # Direct database update or in-memory notification
        owners = ResearchOwner.objects.filter(
            # Add your business logic for owner selection
            is_active=True
        )
        
        for owner in owners:
            self._create_pending_review(owner, iteration)
    
    def _create_pending_review(self, owner: ResearchOwner, iteration: ReformulatedResearchQuestionIteration):
        # Create direct notification record
        from design.models import PendingReview  # Assuming this model exists
        PendingReview.objects.create(
            research_owner=owner,
            iteration=iteration,
            status='pending'
        )


class AsyncNotification(InternalNotificationStrategy):
    """Asynchronous notification using Celery within design module"""
    
    def notify_research_owner(self, iteration: ReformulatedResearchQuestionIteration) -> None:
        notify_owner_task.delay(iteration.id)


class DesignInternalNotification:
    """Orchestrator for internal notifications within design module"""
    
    def __init__(self, strategy: InternalNotificationStrategy = None):
        self._strategy = strategy or DirectNotification()
    
    def notify_new_draft_for_review(self, iteration: ReformulatedResearchQuestionIteration):
        """Handle internal notification when draft is ready for review"""
        self._strategy.notify_research_owner(iteration)