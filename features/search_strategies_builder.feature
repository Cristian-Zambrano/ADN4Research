# SEGUN EL MVP
Feature: Building Structured Search Strings
    As a researcher,
    I want to build my search chain based on my refined research questions,
    So that I can retrieve relevant papers that contribute to my research.

    # Esto para el MVP
    Scenario: Build structured search string with token editing
        Given I have an approved research question
        And the question is tokenized into singular and plural nouns
        When I edit, add, or remove tokens in the visual token list
        And I combine them using logical operators in the drag and drop builder
        Then I should generate a structured search string
        And the system will send the string to the managing papers module
        And the search string will be stored in the research question history linked to its approved research question

    # Esto para el MVP
    Scenario: Build an empty search string
        Given I do not have a refined question list
        When I do not write any tokens or operators
        Then the system should prevent the generation of an empty search string
        And I should see a message "Cannot generate an empty search string"
        And no search string should be stored in the research question history

    Scenario: Build a beta search string using only operators
        Given I do not have a refined question list
        When I write a search string manually using logical operators
        Then I should generate a beta search string
        And the system will send the string to the managing papers module
        And the search string will be stored in the research question history as a "beta"
    
    