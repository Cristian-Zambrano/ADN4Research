from behave import given, when, then, step

@given('there are research question versions with status "SUGGESTED" awaiting validation')
def step_impl(context):
    pass

@when('the owner approves a draft with the justification "{justification}"')
def step_impl(context, justification):
    pass

@then('the question status should change from "{question_status}" to "{new_status}"')
def step_impl(context, question_status, new_status):
    pass

@step('a history record should be created with approver, justification, and date')
def step_impl(context):
    pass

@step('all other researchers should receive a notification of the "{new_status}" question')
def step_impl(context, new_status):
    pass


# Segundo escenario reutilizando los pasos anteriores

@when('the owner rejects a draft with the justification "{justification}"')
def step_impl(context, justification):
    pass

# Tercer escenario reutilizando los pasos anteriores
@when('the owner tries to validate an "{question_status}" version again')
def step_impl(context, question_status):
    pass

@then('the system should raise a "{error_type}" indicating revalidation is not allowed')
def step_impl(context, error_type):
    pass

