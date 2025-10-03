# SEGUN EL MVP
Feature: Managing the lifecycle of research questions (crear → refinar → aprobar → versionar)
    As a researcher,
    I want to refine, version, and validate my research questions using structured frameworks,
    So that I maintain clarity, traceability, and accountability throughout the systematic review.

    # Esto para el MVP
    Scenario: Refine a research question using a <framework> research framework
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        When I complete all the <framework> fields
        Then a refined version of the question should be generated including:
        | element               |
        | the original question |
        | the completed fields  |
        | the reformulated question |
        And the refined version should be stored in the research question history as a "draft"
    Examples:
        | framework | fields                                        |
        | PICO      | Population, Intervention, Comparison, Outcome |
        | PCC       | Population, Concept, Context                  |
        | PEO       | Population, Exposure, Outcome                 |

    # Esto para el MVP
    Scenario: Attempt to refine a research question with incomplete framework fields
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        When I complete only Population and Intervention fields of the <framework>
        Then the system should generate a partial refinement including:
        | element               |
        | the original question |
        | the partially completed fields |
        And the refinement should be stored in the research question history as an "incomplete draft"
        And the incomplete draft should not be eligible for submission to the owner
    Examples:
        | framework | fields                                        |
        | PICO      | Population, Intervention, Comparison, Outcome |
        | PCC       | Population, Concept, Context                  |
        | PEO       | Population, Exposure, Outcome                 |

    Scenario: Send a refined research question for approval
        Given I have a refined draft research question generated with the PICO framework
        When I send the refined question for approval to the research team via communication bus
        And the owner approves the question with the justification "Aligned with project objectives"
        Then the question status should be updated to "approved"
        And the approval record should store the approver, justification, and approval date
        And all other researchers should receive a notification of the submission
    
    #Preguntar si esto puede ser un paso del escenario negativo 1 o esta bien como independiente
    Scenario: Attempt to send an incomplete draft research question for approval 
        Given I have an incomplete draft research question generated with the PICO framework
        When I attempt to send the incomplete draft for approval to the research team
        Then the system should prevent the submission
        And I should see a message "The research question cannot be sent for approval until all framework fields are completed"
        And the question should remain stored in the research question history as an "incomplete draft"

    # Un escenario puede evolucionar en sus pasos cuando se avanza en la entrega de funcionalidades? (mas "MVPs") 
    Scenario: Track the version history of a research question
        Given I have an original research question "¿Cómo influye la tecnología en la educación?"
        And I generate multiple refinements of the question using the PICO framework
        And each refinement is submitted and approved by the research owner
        When I view the version history of the research question
        Then I should see all versions in chronological order
        And each version should display: author, framework used, approver, justification, and timestamp
        And all drafts derived from the original question should be included