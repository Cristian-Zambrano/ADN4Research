# serializers.py
from design.models import ResearchQuestionVersion
from rest_framework import serializers

class QuestionSubmissionSerializer(serializers.Serializer):
    """Valida los datos de entrada para la creación de una nueva versión."""
    framework = serializers.ChoiceField(choices=ResearchQuestionVersion.FrameworkChoices.choices)
    fields = serializers.JSONField()
    reformulated_text = serializers.CharField()
    
    # Aquí se podrían añadir validaciones más complejas,
    # por ejemplo, asegurar que el JSON 'fields' contiene las claves correctas para el 'framework' dado.
class DraftQuestionVersionSerializer(serializers.Serializer):
    """Serializador para validar los datos de un borrador de pregunta de investigación."""
    framework = serializers.CharField(max_length=4)
    fields = serializers.JSONField()
    reformulated_text = serializers.CharField(allow_blank=True)

class QuestionVersionResponseSerializer(serializers.ModelSerializer):
    """Formatea la salida de un objeto ResearchQuestionVersion para la API."""
    fields = serializers.JSONField(source='framework_fields')

    class Meta:
        model = ResearchQuestionVersion
        fields = ['id', 'framework', 'fields', 'reformulated_text', 'status', 'submitted_at']

class ValidationJustificationSerializer(serializers.Serializer):
    """Valida la justificación requerida para aprobar/rechazar una versión."""
    justification = serializers.CharField(min_length=10)