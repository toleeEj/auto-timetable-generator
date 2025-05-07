from django.urls import path
from . import views

urlpatterns = [
    path('feedback/', views.submit_feedback, name='submit_feedback'),
    path('feedback/list/', views.feedback_list, name='feedback_list'),
    path('feedback/<int:feedback_id>/', views.feedback_detail, name='feedback_detail'),
    path('feedback/<int:feedback_id>/delete/', views.feedback_delete, name='feedback_delete'),
]