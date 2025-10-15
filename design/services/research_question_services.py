# services/design_service.py
from design.exceptions.exceptions import AlreadyValidatedException, InvalidStatusForValidationException, QuestionNotFoundException, QuestionVersionNotFoundException, SubmissionError, UnauthorizedValidationException
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
        parent_question = ResearchQuestion.objects.get(id=question_id)
    except ResearchQuestion.DoesNotExist:
        raise QuestionNotFoundException(question_id=question_id)
    # Esto para cuando ya haya gestion de usuarios y proyectos
    #if not parent_question.project.is_member(researcher):
    #    raise UnauthorizedSubmissionException(project_name=parent_question.project.name)
    
    # Aquí iría validación de permisos del investigador (futura implementación)
    
    last_version = parent_question.versions.order_by('-iteration_number').first()
    new_iteration_number = (last_version.iteration_number + 1) if last_version else 1

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

    notification_service.dispatch_notification_for_review(version=new_version)

    return new_version

@transaction.atomic
def save_question_draft(
    *,
    researcher: User,
    question_id: int,
    framework: str,
    fields: dict,
    reformulated_text: str
) -> ResearchQuestionVersion:
    try:
        parent_question = ResearchQuestion.objects.get(id=question_id)
    except ResearchQuestion.DoesNotExist:
        raise QuestionNotFoundException(question_id=question_id)
    # Esto para cuando ya haya gestion de usuarios y proyectos
    #if not parent_question.project.is_member(researcher):
    #    raise UnauthorizedSubmissionException(project_name=parent_question.project.name)

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
    
@transaction.atomic
def approve_question_version(
    *,
    validator: User,
    question_id: int,
    version_id: int,
    justification: str
) -> ResearchQuestionVersion:
    try:
        version = ResearchQuestionVersion.objects.select_related('question__project').get(
            id=version_id, 
            question__id=question_id
        )
    except ResearchQuestionVersion.DoesNotExist:
        raise QuestionVersionNotFoundException(version_id=version_id, question_id=question_id)

    # Validación 1: No permitir revalidación
    if version.status in [
        ResearchQuestionVersion.StatusChoices.APPROVED,
        ResearchQuestionVersion.StatusChoices.REJECTED
    ]:
        raise AlreadyValidatedException()

    # Validación 2: Solo se pueden aprobar versiones en estado SUGGESTED
    if version.status != ResearchQuestionVersion.StatusChoices.SUGGESTED:
        raise InvalidStatusForValidationException(
            current_status=version.status,
            required_status="SUGGESTED"
        )

    # Validación 3: Solo el dueño del proyecto puede aprobar
    if version.question.project.owner != validator:
        raise UnauthorizedValidationException()

    # Transición de estado (regla de negocio principal)
    version.status = ResearchQuestionVersion.StatusChoices.APPROVED
    version.save()

    # Registrar historial de validación
    version.validation_history.create(
        validator=validator,
        action='APPROVED',
        justification=justification
    )

    # Despachar notificación
    notification_service.dispatch_notification_for_approval(version=version)

    return version

@transaction.atomic
def reject_question_version(
    *,
    validator: User,
    question_id: int,
    version_id: int,
    justification: str
) -> ResearchQuestionVersion:
    try:
        version = ResearchQuestionVersion.objects.select_related('question__project').get(
            id=version_id, 
            question__id=question_id
        )
    except ResearchQuestionVersion.DoesNotExist:
        raise QuestionVersionNotFoundException(version_id=version_id, question_id=question_id)

    # Validación 1: No permitir revalidación
    if version.status in [
        ResearchQuestionVersion.StatusChoices.APPROVED,
        ResearchQuestionVersion.StatusChoices.REJECTED
    ]:
        raise AlreadyValidatedException()

    # Validación 2: Solo se pueden rechazar versiones en estado SUGGESTED
    if version.status != ResearchQuestionVersion.StatusChoices.SUGGESTED:
        raise InvalidStatusForValidationException(
            current_status=version.status,
            required_status="SUGGESTED"
        )

    # Validación 3: Solo el dueño del proyecto puede rechazar
    if version.question.project.owner != validator:
        raise UnauthorizedValidationException()

    # Transición de estado
    version.status = ResearchQuestionVersion.StatusChoices.REJECTED
    version.save()

    # Registrar historial de validación
    version.validation_history.create(
        validator=validator,
        action='REJECTED',
        justification=justification
    )

    # Despachar notificación (si se implementa)
    notification_service.dispatch_notification_for_rejection(version=version)

    return version