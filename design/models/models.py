from django.db import models
from django.forms import JSONField

# Create your models here.

class Researcher(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class ResearchQuestion(models.Model):
    original_text = models.TextField()
    created_by = models.ForeignKey('Researcher', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.original_text[:50]
    
class Framework(models.Model):
    name = models.CharField(max_length=50)
    fields = models.JSONField()  # Ej: {"P": "Population", "I": "Intervention", "C": "Comparison", "O": "Outcome"}


class ReformulatedResearchQuestionIteration(models.Model):
    STATUS_CHOICES = [
        ('incomplete_draft', 'Incomplete Draft'),
        ('to_review', 'To Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    researcher = models.ForeignKey(Researcher, on_delete=models.PROTECT)
    research_question = models.ForeignKey(ResearchQuestion, on_delete=models.CASCADE, related_name='refinements')
    framework = models.ForeignKey(Framework, on_delete=models.PROTECT)
    filled_fields = models.JSONField(default=dict)  # {'Population': '...', ...}
    reformulated_research_question = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    iteration_number = models.PositiveIntegerField()
    created_by = models.ForeignKey(Researcher, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    