from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.feedback_list, name='list'),
    path('create/', views.create_feedback, name='create'),
    path('<uuid:feedback_id>/edit/', views.edit_feedback, name='edit'),
    path('<uuid:feedback_id>/delete/', views.delete_feedback, name='delete'),
    path('dismiss-modal/', views.dismiss_modal, name='dismiss_modal'),
    path('check-modal/', views.check_should_show_modal, name='check_modal'),
]

