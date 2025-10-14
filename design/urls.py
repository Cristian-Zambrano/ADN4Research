from django.urls import include, path
from design.views import ApproveQuestionVersionAPIView, RejectQuestionVersionAPIView, SubmitQuestionVersionAPIView, SaveDraftAPIView


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
    path(
        'questions/<int:question_id>/versions/<int:version_id>/approve/',
        ApproveQuestionVersionAPIView.as_view(),
        name='approve-question-version'
    ),
    
    # Rechazo de versión por el dueño del proyecto
    path(
        'questions/<int:question_id>/versions/<int:version_id>/reject/',
        RejectQuestionVersionAPIView.as_view(),
        name='reject-question-version'
    ),
]
