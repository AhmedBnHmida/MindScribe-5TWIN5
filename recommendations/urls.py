from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Recommendations
    path('list/', views.recommendations_list, name='list'),
    path('generate/', views.generate_recommendations, name='generate'),
    path('<uuid:recommendation_id>/status/', views.update_recommendation_status, name='update_status'),
    
    # Goals (Objectifs)
    path('goals/', views.goals_list, name='goals'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('goals/<uuid:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<uuid:goal_id>/progress/', views.update_goal_progress, name='update_goal_progress'),
    path('goals/<uuid:goal_id>/delete/', views.delete_goal, name='delete_goal'),
]

