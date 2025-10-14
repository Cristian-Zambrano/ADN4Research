from django.urls import include, path
from design.views import SubmitQuestionVersionAPIView, SaveDraftAPIView


urlpatterns = [
    path(
        'questions/<int:question_id>/submit/', 
        SubmitQuestionVersionAPIView.as_view(), 
        name='submit-question-version'
    ),
    path(
        'questions/<int:question_id>/draft/',
        SaveDraftAPIView.as_view(),
        name='save-draft-version'
    ),
]
