# Ciclo de vida de las preguntas de investigación (crear → reformular → aprobar → versionar)
# Reformular: hacer la pregunta más precisa, específica y bien definida mediante marcos de trabajo investigativos
# Submit to the owner for approval
# incomplete draftw: estado de la PI que solo tiene pregunta base, framework y campos parcialmente llenos.
# draft for review: estado de la pregunta de investigacion enviada que incluye: pregunta base, framework, campos rellenos y pregunta reestructurada, para revision
# based on the framework fields provided PREGUNTAR ESTO PARA EL PASO DEL AND | INTEGRACION CON IA para provar
Feature: Managing the lifecycle of research questions
    As a researcher
    I want to maintain control over the evolution of my research questions
    So that I can ensure their proper validation throughout the systematic review.

    Scenario Outline: Submit a reformulated research question for review
        Given I have an assigned task to propose research questions for the current project
        When I submit the draft question for review with the following data
        """
            {
                "framework": "<framework>",
                "fields": { <fields> },
                "reformulated_text": "<reformulated_text>"
            }
            """
        Then a new version of the question should be created with its status set to "suggested"
        And the new version data must match the submitted data
        And a notification request should be dispatched to the communication module

        Examples:
            | framework | fields                                                    | reformulated_text                                                               |
            | PICO      | "Population": "X", "Intervention": "Y", "Comparison": "Z" | ¿Cuál es el efecto de Y en comparación con Z en la población X?               |
            | PEO       | "Population": "A", "Exposure": "B", "Outcome": "C"        | ¿Cuál es la relación entre la exposición B y el resultado C en la población A? |

# Esto para el MVP | se considera como guardado automatico, el boton de publicar es del escenario 1
    Scenario Outline: Autosave an incomplete research question draft
        Given I am working on a research question for the "<framework>" framework
        When the system receives a request to save a draft with the following data
            """
            {
            "fields": { <partially_completed_fields> },
            "reformulated_text": "<reformulated_text>"
            }
            """
        Then a research question version must exist with status "DRAFT"
        And its data must match the submitted draft data
        And no notification for review should be sent

        Examples:
            | framework | partially_completed_fields                               | reformulated_text                                  |
            | PICO      | "Population": "Adult patients", "Intervention": "Aspirin" | Para pacientes adultos, ¿es la aspirina...       |
            | PCC       | "Population": "Pediatric nurses"                         |                                                  |
            | PEO       | "Population": "Office workers", "Outcome": "Stress levels" | ¿Cómo afecta... a los trabajadores de oficina? |

'''
    # Un escenario puede evolucionar en sus pasos cuando se avanza en la entrega de funcionalidades? (mas "MVPs") 
    Scenario: Track the version history of a research question
        Given I have an original research question "¿Cómo influye la tecnología en la educación?"
        And I generate multiple refinements of the question using the PICO framework
        And each refinement is submitted and approved by the research owner
        When I view the version history of the research question
        Then I should see all versions in chronological order
        And each version should display: author, framework used, approver, justification, and timestamp
        And all the states of the research question derived from the original question should be included
'''