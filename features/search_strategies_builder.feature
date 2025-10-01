# SEGUN EL MVP
Feature: Building Structured Search Strings
    As a researcher,
    I want to build my search chain based on my review protocol,
    So that I can retrieve relevant papers that contribute to my research.

    Scenario: Generate a search string from inclusion and exclusion criteria
        Given I have a "completed" research question
        When I define the inclusion and exclusion criteria for my review
        Then I should see a generated search string that includes the selected inclusion and exclusion parameters
