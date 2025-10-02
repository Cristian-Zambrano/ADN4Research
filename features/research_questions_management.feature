# SEGUN EL MVP
Feature: Managing the lifecycle of research questions (crear → refinar → aprobar → versionar)
    As a researcher,
    I want to refine, version, and validate my research questions using structured frameworks,
    So that I maintain clarity, traceability, and accountability throughout the systematic review.

    Scenario: Refine a research question using a <framework> research framework
        Given I have the research question "¿Cómo influye la tecnología en la educación?"
        When I complete the <framework> fields
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

    Scenario: Send a refined research question for approval
        Given I have a refined draft research question generated with the PICO framework
        When I send the refined question for approval to the research team via communication bus
        Then the owner approves the question with the justification "Aligned with project objectives"
        And the question status should be updated to "approved"
        And the approval record should store the approver, justification, and approval date
        And all other researchers should receive a notification of the submission

    Scenario: Track the version history of a research question
        Given I have an original research question "¿Cómo influye la tecnología en la educación?"
        And I generate multiple refinements of the question using the PICO framework
        And each refinement is submitted and approved by the research owner
        When I view the version history of the research question
        Then I should see all versions in chronological order
        And each version should display: author, framework used, approver, justification, and timestamp
        And all drafts derived from the original question should be included