from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .pagination import CategoryCursorPagination, CustomCursorPagination

from .models import Category, SubTask, Task
from .serializers import (
    CategoryCreateSerializer,
    SubTaskCreateSerializer,
    SubTaskSerializer,
    TaskSerializer,
)

WEEKDAYS = {
    'понедельник': 2,
    'вторник': 3,
    'среда': 4,
    'четверг': 5,
    'пятница': 6,
    'суббота': 7,
    'воскресенье': 1,
}


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # только авторизованные пользователи
def task_stats(request):
    """Возвращает статистику по задачам: общее количество, статусы, просроченные."""
    now = timezone.now()
    total_tasks = Task.objects.count()
    status_counts = dict(
        Task.objects.values_list('status').annotate(count=Count('id'))
    )
    overdue_tasks = Task.objects.filter(
        deadline__lt=now,
    ).exclude(
        status='done',
    ).count()

    return Response({
        'total_tasks': total_tasks,
        'status_counts': status_counts,
        'overdue_tasks': overdue_tasks,
    })


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/tasks/ — список задач (доступно всем)
    POST /api/tasks/ — создание задачи (только авторизованным)
    Поддерживает фильтрацию: ?day=понедельник&status=new&deadline=2026-07-01
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # чтение — всем, запись — авторизованным
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        qs = Task.objects.all()
        day = self.request.query_params.get('day')
        if day:
            num = WEEKDAYS.get(day.lower())
            if num:
                qs = qs.filter(deadline__week_day=num)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        deadline = self.request.query_params.get('deadline')
        if deadline:
            qs = qs.filter(deadline=deadline)
        return qs


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/<id>/ — просмотр задачи (доступно всем)
    PUT    /api/tasks/<id>/ — полное обновление задачи (только авторизованным)
    PATCH  /api/tasks/<id>/ — частичное обновление (только авторизованным)
    DELETE /api/tasks/<id>/ — удаление задачи (только авторизованным)
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # чтение — всем, запись — авторизованным
    lookup_field = 'id'


class SubTaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/subtasks/ — список подзадач (доступно всем)
    POST /api/subtasks/ — создание подзадачи (только авторизованным)
    Поддерживает фильтрацию: ?task_title=...&status=new&deadline=...
    """
    queryset = SubTask.objects.select_related('task').all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # чтение — всем, запись — авторизованным
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        qs = SubTask.objects.select_related('task').all()
        task_title = self.request.query_params.get('task_title')
        if task_title:
            qs = qs.filter(task__title__icontains=task_title)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        deadline = self.request.query_params.get('deadline')
        if deadline:
            qs = qs.filter(deadline=deadline)
        return qs


class SubTaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/subtasks/<id>/ — просмотр подзадачи (доступно всем)
    PUT    /api/subtasks/<id>/ — полное обновление (только авторизованным)
    PATCH  /api/subtasks/<id>/ — частичное обновление (только авторизованным)
    DELETE /api/subtasks/<id>/ — удаление (только авторизованным)
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # чтение — всем, запись — авторизованным
    lookup_field = 'id'


class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/categories/ — список категорий (доступно всем)
    POST   /api/categories/ — создание категории (только авторизованным)
    GET    /api/categories/<id>/ — просмотр категории (доступно всем)
    PUT    /api/categories/<id>/ — обновление категории (только авторизованным)
    DELETE /api/categories/<id>/ — удаление категории (только авторизованным)
    GET    /api/categories/count_tasks/ — количество задач в каждой категории
    """
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # чтение — всем, запись — авторизованным
    pagination_class = CategoryCursorPagination

    @action(detail=False, methods=['get'])
    def count_tasks(self, request):
        """Возвращает список категорий с количеством задач в каждой."""
        categories = self.get_queryset().annotate(task_count=Count('tasks'))
        return Response([
            {'id': c.id, 'name': c.name, 'task_count': c.task_count}
            for c in categories
        ])
