# SEGUN EL MVP
Feature: Building Structured Search Strings
    As a researcher
    I want to build my search string based on my refined research questions
    So that I can retrieve relevant papers that contribute to my research.

    # Esto para el MVP
    Scenario: Build structured search string draft with token editing
        Given I have an approved research question
        And the question is tokenized into singular and plural nouns
        When I edit, add, or remove tokens in the visual token list
        And I combine them using logical operators in the drag and drop builder
        Then I should generate a structured search string
        And the system will store the search string in the research question history as a "structured search string draft" including:
        | element                            |
        | the research question              |
        | the resulting search string        |
        | the timestamp of the search string |

    # Esto para el MVP
    Scenario: Build a beta search string using only operators
        Given I do not have a refined question list
        When I write a search string manually using logical operators
        Then I should generate a beta search string
        And the system will store the search string in the research question history as a "beta" including
        | element                            |
        | the resulting search string        |
        | the timestamp of the search string |
        
    Scenario: Execute the search string and display results
        Given I have a defined search string (refined or beta)
        When I submit the search string 
        And the managing papers module returns the metadata results
        Then the system will display the resulting papers
        And the system will store the search string in the research question history including:
        | element                               |
        | the research question (if structured) |
        | the resulting search string           |
        | the timestamp of the search string    |
        | the results of the search string      |
