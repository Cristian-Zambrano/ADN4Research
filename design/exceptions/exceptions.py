class DesignDomainException(Exception):
    """
    Excepción base para todos los errores de dominio del módulo 'design'.
    Hereda de Exception para mantener compatibilidad con el sistema de excepciones de Python.
    """
    pass

# --- Excepciones de Sumisión ---

class SubmissionError(DesignDomainException):
    """
    Error al intentar someter una versión de pregunta para revisión.
    Incluye casos como:
    - Pregunta de investigación no existe
    - Usuario no tiene permisos para someter
    - Datos de sumisión inválidos
    """
    pass


class DraftSaveError(DesignDomainException):
    """
    Error al intentar guardar un borrador de pregunta.
    """
    pass


# --- Excepciones de Validación ---

class ValidationError(DesignDomainException):
    """
    Excepción base para errores relacionados con validación de versiones.
    """
    pass


class AlreadyValidatedException(ValidationError):
    """
    Se lanza cuando se intenta validar (aprobar/rechazar) una versión
    que ya ha sido validada previamente (estado APPROVED o REJECTED).
    
    HTTP mapping: 400 Bad Request
    """
    def __init__(self):
        super().__init__("This version has already been validated and cannot be revalidated.")


class InvalidStatusForValidationException(ValidationError):
    """
    Se lanza cuando se intenta validar una versión que no está en estado SUGGESTED.
    Por ejemplo, intentar aprobar una versión en estado DRAFT.
    
    HTTP mapping: 400 Bad Request
    """
    def __init__(self, current_status: str, required_status: str = "SUGGESTED"):
        self.current_status = current_status
        self.required_status = required_status
        super().__init__(
            f"Cannot validate version in status {current_status}. "
            f"Only {required_status} versions can be validated."
        )


class UnauthorizedValidationException(ValidationError):
    """
    Se lanza cuando un usuario intenta validar una versión sin tener permisos.
    Solo el dueño del proyecto puede validar versiones.
    
    HTTP mapping: 403 Forbidden
    """
    def __init__(self):
        super().__init__("You do not have permission to validate this version.")


# --- Excepciones de Recursos ---

class ResourceNotFoundError(DesignDomainException):
    """
    Error genérico para recursos no encontrados en el módulo 'design'.
    HTTP mapping: 404 Not Found
    """
    pass


class QuestionNotFoundException(ResourceNotFoundError):
    """
    Se lanza cuando no se encuentra una pregunta de investigación por su ID.
    """
    def __init__(self, question_id: int):
        self.question_id = question_id
        super().__init__(f"Research question with id={question_id} does not exist.")


class QuestionVersionNotFoundException(ResourceNotFoundError):
    """
    Se lanza cuando no se encuentra una versión de pregunta por su ID.
    """
    def __init__(self, version_id: int, question_id: int = None):
        self.version_id = version_id
        self.question_id = question_id
        message = f"Research question version with id={version_id} does not exist"
        if question_id:
            message += f" for question {question_id}"
        super().__init__(message + ".")