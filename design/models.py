from django.db import models
from django.conf import settings

class ResearchQuestion(models.Model):
    """Representa la pregunta de investigación principal y su estado general."""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='research_questions')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
class ResearchQuestionVersion(models.Model):
    """Almacena una versión inmutable y específica de una ResearchQuestion."""
    class StatusChoices(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUGGESTED = 'SUGGESTED', 'Suggested'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    class FrameworkChoices(models.TextChoices):
        PICO = 'PICO', 'PICO'
        PCC = 'PCC', 'PCC'
        PEO = 'PEO', 'PEO'

    # Relaciones y Metadatos
    question = models.ForeignKey(ResearchQuestion, on_delete=models.CASCADE, related_name='versions')
    parent_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    researcher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='question_versions')
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    iteration_number = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True) # Corresponde a 'timestamp'

    # Datos del Escenario
    framework = models.CharField(max_length=4, choices=FrameworkChoices.choices)
    reformulated_text = models.TextField(blank=True, default='')
    # Usamos JSONField para flexibilidad máxima con los campos del framework
    framework_fields = models.JSONField()

    def __str__(self):
        return f"{self.question.id} - v{self.iteration_number} ({self.get_status_display()})"

class Task(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='desing_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
