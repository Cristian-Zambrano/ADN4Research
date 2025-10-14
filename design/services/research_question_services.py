# services/design_service.py
from design.exceptions.exceptions import SubmissionError
from design.services import notification_service
from ..models import ResearchQuestionVersion, ResearchQuestion
from django.contrib.auth.models import User
from django.db import transaction

@transaction.atomic
def submit_question_for_review(
    *,
    researcher: User,
    question_id: int,
    framework: str,
    fields: dict,
    reformulated_text: str
) -> ResearchQuestionVersion:
    """
    Crea una nueva versión de una PI y la somete a revisión.
    Este método encapsula toda la lógica descrita en el escenario.
    """
    try:
        # 1. Validar y obtener la pregunta principal y la última versión
        parent_question = ResearchQuestion.objects.get(id=question_id)
        # Aquí iría la lógica para validar permisos del investigador
        
        last_version = parent_question.versions.order_by('-iteration_number').first()
        new_iteration_number = (last_version.iteration_number + 1) if last_version else 1

        # 2. Crear la nueva versión (el "Then" del escenario)
        new_version = ResearchQuestionVersion.objects.create(
            question=parent_question,
            parent_version=last_version,
            researcher=researcher,
            status=ResearchQuestionVersion.StatusChoices.SUGGESTED,
            iteration_number=new_iteration_number,
            framework=framework,
            framework_fields=fields,
            reformulated_text=reformulated_text
        )

        # 3. Despachar la notificación (el último "And" del escenario)
        # Esto invoca al "Design Bus Adapter"
        notification_service.dispatch_notification_for_review(version=new_version)

        return new_version

    except ResearchQuestion.DoesNotExist:
        raise SubmissionError("La pregunta de investigación no existe.")
    except Exception as e:
        # Capturar otros posibles errores para no exponer detalles de implementación
        raise SubmissionError(f"Error al procesar la solicitud: {e}")
@transaction.atomic
def save_question_draft(
    *,
    researcher: User,
    question_id: int,
    framework: str,
    fields: dict,
    reformulated_text: str
) -> ResearchQuestionVersion:
    print("Saving draft...")
    print(fields)
    try:
        parent_question = ResearchQuestion.objects.get(id=question_id)
        draft_version, created = ResearchQuestionVersion.objects.update_or_create(
            question=parent_question,
            researcher=researcher,
            status=ResearchQuestionVersion.StatusChoices.DRAFT,
            defaults={
                'framework': framework.upper(),
                'framework_fields': fields,
                'reformulated_text': reformulated_text
            }
        )

        return draft_version

    except ResearchQuestion.DoesNotExist:
        raise SubmissionError(f"La pregunta de investigación con id={question_id} no existe.")
    except Exception as e:
        raise SubmissionError(f"Error al guardar el borrador: {e}")