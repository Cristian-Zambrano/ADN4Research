from django.db import models
from django.contrib.auth.models import User

class Researcher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class ResearchOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class ResearchQuestion(models.Model):
    original_text = models.TextField()
    created_by = models.ForeignKey('Researcher', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.original_text[:50]

class Framework(models.Model):
    name = models.CharField(max_length=50)
    fields = models.JSONField()

class ReformulatedResearchQuestionIteration(models.Model):
    STATUS_CHOICES = [
        ('incomplete_draft', 'Incomplete Draft'),
        ('to_review', 'To Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    researcher = models.ForeignKey(Researcher, on_delete=models.PROTECT, related_name='iterations_as_researcher')
    research_question = models.ForeignKey(ResearchQuestion, on_delete=models.CASCADE, related_name='refinements')
    framework = models.ForeignKey(Framework, on_delete=models.PROTECT)
    filled_fields = models.JSONField(default=dict)
    reformulated_research_question = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    iteration_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class ApprovalCenter(models.Model):
    owner = models.OneToOneField('ResearchOwner', on_delete=models.CASCADE, related_name='approval_center')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [models.Index(fields=['owner'])]

class ApprovalItem(models.Model):
    approval_center = models.ForeignKey('ApprovalCenter', on_delete=models.CASCADE, related_name='items')
    iteration = models.ForeignKey('ReformulatedResearchQuestionIteration', on_delete=models.CASCADE, related_name='approval_items')
    submitted_by = models.ForeignKey('Researcher', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('approval_center', 'iteration')
        indexes = [models.Index(fields=['approval_center', 'submitted_at']),
                   models.Index(fields=['iteration'])]

class ResearchQuestionHistory(models.Model):
    research_question = models.ForeignKey(ResearchQuestion, on_delete=models.CASCADE, related_name='history_entries')
    iteration = models.ForeignKey(ReformulatedResearchQuestionIteration, on_delete=models.CASCADE)
    recorded_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('research_question', 'iteration')
        indexes = [models.Index(fields=['research_question', 'recorded_at'])]
    @classmethod
    def is_iteration_in_history(cls, iteration_id: int) -> bool:
        return cls.objects.filter(iteration_id=iteration_id).exists()