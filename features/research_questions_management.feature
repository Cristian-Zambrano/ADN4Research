# SEGUN EL MVP
Feature: Managing Research Questions
    As a researcher,
    I want to manage my research questions using structured frameworks,
    To ensure clarity and focus throughout my systematic literature review.

    Scenario: Trace the evolution of a research question using PICO
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        When I complete the PICO framework fields for the question
        And I mark the question as "completed" # Preguntar si existe una validacion de estas preguntas con el owner
        Then I should see both the original and refined versions of the question in the evolution trace
    
    Scenario: Identifying incomplete research question # Esto puede que no vaya o solo sea un step de algun otro scenario
        Given I am preparing a research question
        When I omit one or more PICO elements
        Then the system highlights the missing components

    

