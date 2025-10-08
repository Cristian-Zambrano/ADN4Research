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
    Scenario Outline: Publish a reformulated research question as a draft for review
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
'''
    
        '''