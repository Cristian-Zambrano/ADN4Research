Feature: Validate the researchers research question 
    As an owner of the research project
    I want to maintain control over the research questions of the project
    So that I can ensure a proper validation of them and keep a traceable history.

    Scenario: Research owner approves a research question
        Given there are research question versions with status "SUGGESTED" awaiting validation
        When the owner "approve" a draft with the justification "Aligned with project objectives"
        Then the question status should change from "SUGGESTED" to "APPROVED"
        And a history record should be created with approver, justification, and date
        And all other researchers should receive a notification of the "APPROVED" question

    Scenario: Research owner rejects a research question
        Given there are research question versions with status "SUGGESTED" awaiting validation
        When the owner "reject" a draft with the justification "Not aligned with project objectives"
        Then the question status should change from "SUGGESTED" to "REJECTED"
        And a history record should be created with approver, justification, and date
        And all other researchers should receive a notification of the "REJECTED" question
    
    Scenario: Research owner attempts to revalidate an already approved question
        Given there are research question versions with status "SUGGESTED" awaiting validation
        When the owner tries to validate an "APPROVED" version again
        Then the system should raise a "SubmissionError" indicating revalidation is not allowed