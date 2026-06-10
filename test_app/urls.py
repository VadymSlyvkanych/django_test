from django.urls import path
from . import views


urlpatterns = [
    path('api/tasks/stats/', views.task_stats, name='task-stats'),
    path('api/tasks/<int:id>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('api/tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('api/subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('api/subtasks/<int:id>/', views.SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask-detail-update-delete'),
]
