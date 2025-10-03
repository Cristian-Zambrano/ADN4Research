# Ciclo de vida de las preguntas de investigación (crear → refinar → aprobar → versionar)
# Refinar: hacer la pregunta más precisa, específica y bien definida mediante marcos de trabajo investigativos
# Publish: sent to owner for approval
Feature: Managing the lifecycle of research questions
    As a researcher
    I want to maintain control over the evolution of my research questions
    So that I can ensure their proper validation throughout the systematic review.

    # Esto para el MVP
    Scenario: Publish a refined research question as a draft for review
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        When I complete all the <framework> fields
        Then a refined version of the question should be generated including:
        | element                   |
        | the original question     |
        | the completed fields      |
        | the reformulated question |
        And the refined version should be stored in the research question history as a "draft for review"
        And the system should send the draft to the research owner for review
        And the draft should be published on the approvement center
    Examples:
        | framework | fields                                        |
        | PICO      | Population, Intervention, Comparison, Outcome |
        | PCC       | Population, Concept, Context                  |
        | PEO       | Population, Exposure, Outcome                 |

    # Esto para el MVP | se considera como guardado automatico, el boton de publicar es del escenario 1
    Scenario: Save a partially completed research question draft
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        When I dont complete all the fields of the <framework> to refined it
        Then the system should generate a partial refinement including:
        | element                        |   
        | the original question          |
        | the partially completed fields |
        And the incomplete refinement should be stored in the research question history as an "incomplete draft"
        And the incomplete draft should not be sent for submission to the owner
    Examples:
        | framework | fields                                        |
        | PICO      | Population, Intervention, Comparison, Outcome |
        | PCC       | Population, Concept, Context                  |
        | PEO       | Population, Exposure, Outcome                 |

    Scenario: Research owner approves a research question
        Given at least one research question draft on the approvement center
        When the owner approves a draft with the justification "Aligned with project objectives"
        Then the draft status should be updated to "approved"
        And the approval record should store in the research question history with: approver, justification, and approval date
        And all other researchers should receive a notification of the approval

    Scenario: Research owner rejects a research question
        Given at least one research question draft on the approvement center
        When the owner rejects a draft with the justification "Not aligned with project objectives"
        Then the draft status should be updated to "rejected"
        And all other researchers should receive a notification of the rejection

    # Un escenario puede evolucionar en sus pasos cuando se avanza en la entrega de funcionalidades? (mas "MVPs") 
    Scenario: Track the version history of a research question
        Given I have an original research question "¿Cómo influye la tecnología en la educación?"
        And I generate multiple refinements of the question using the PICO framework
        And each refinement is submitted and approved by the research owner
        When I view the version history of the research question
        Then I should see all versions in chronological order
        And each version should display: author, framework used, approver, justification, and timestamp
        And all the states of the research question derived from the original question should be included