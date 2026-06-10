from django.urls import path
from . import views


urlpatterns = [
    path('api/tasks/stats/', views.task_stats, name='task-stats'),
    path('api/tasks/<int:id>/', views.task_detail, name='task-detail'),
    path('api/tasks/', views.task_list, name='task-list'),
    path('api/subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('api/subtasks/<int:id>/', views.SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update-delete'),
]