from django.urls import path
from design import views

urlpatterns = [
    path('design/submit/', views.submit_reformulation, name='design_submit'),
    path('design/owner-inbox/', views.owner_inbox, name='design_owner_inbox'),
]
