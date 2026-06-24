from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/tasks/stats/', views.task_stats, name='task-stats'),
    path('api/tasks/my/', views.UserTaskListView.as_view(), name='user-tasks'),
    path('api/tasks/<int:id>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('api/tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('api/subtasks/', views.SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('api/subtasks/<int:id>/', views.SubTaskRetrieveUpdateDestroyView.as_view(), name='subtask-detail-update-delete'),
    path('api/', include(router.urls)),
]
