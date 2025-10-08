# Ciclo de vida de las preguntas de investigación (crear → reformular → aprobar → versionar)
# Reformular/refinar: hacer la pregunta más precisa, específica y bien definida mediante marcos de trabajo investigativos
# Publish: sent to owner for approval
# incomplete draftw: estado de la PI que solo tiene pregunta base, framework y campos parcialmente llenos.
# draft for review: estado de la pregunta de investigacion enviada que incluye: pregunta base, framework, campos rellenos y pregunta reestructurada, para revision
# based on the framework fields provided PREGUNTAR ESTO PARA EL PASO DEL AND | INTEGRACION CON IA para provar
Feature: Managing the lifecycle of research questions
    As a researcher
    I want to maintain control over the evolution of my research questions
    So that I can ensure their proper validation throughout the systematic review.

    # Esto para el MVP
    Scenario Outline: Publish a reformulated research question for review
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        When I complete all the "<fields>" required by the "<framework>"
        And I provide the reformulated question text
        And I send the draft to the research owner for review
        Then a reformulated version of the question should be stored in the research question history including:
        | element                   |
        | researcher                |
        | the original question     |
        | the framework used        |
        | the completed fields      |
        | the reformulated question |
        | status = to_review        |
        | number of iteration       |
        | timestamp                 |
        And the system should notify the owner about the iteration to approve
    Examples:
        | framework | fields                                        |
        | PICO      | Population, Intervention, Comparison, Outcome |
        | PCC       | Population, Concept, Context                  |
        | PEO       | Population, Exposure, Outcome                 |
        # Cambia no mas esta cosa para ponerlo como publicar que sea el trigger

# Esto para el MVP | se considera como guardado automatico, el boton de publicar es del escenario 1
    Scenario Outline: Save a partially completed research question draft
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        And I choose a framework "<framework>"
        #When I don't complete all the "<fields>" of the "<framework>"
        #Then the system should generate a partial refinement including:
        | element                        |
        | the original question          |
        | the partially completed fields |
        #And the system should stored the draft in the research question history as an "incomplete draft"
        #And the incomplete draft should not be sent for submission to the owner
    Examples:
        | framework | fields                                        |
        | PICO      | Population, Intervention, Comparison, Outcome |
        | PCC       | Population, Concept, Context                  |
        | PEO       | Population, Exposure, Outcome                 |

'''
    Scenario: Research owner approves a research question
        Given at least one research question draft on the approval center
        When the owner approves a draft with the justification "Aligned with project objectives"
        Then the draft status should be updated to "approved"
        And the approval record should store in the research question history with: approver, justification, and approval date
        And all other researchers should receive a notification of the approval

    Scenario: Research owner rejects a research question
        Given at least one research question draft on the approval center
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
        '''