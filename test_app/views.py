from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SubTask, Task
from .serializers import (
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


@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        day = request.query_params.get('day')
        if day:
            day_num = WEEKDAYS.get(day.lower())
            if day_num is None:
                return Response(
                    {'error': f'Invalid day: {day}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            tasks = Task.objects.filter(deadline__week_day=day_num)
        else:
            tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_detail(request, id):
    try:
        task = Task.objects.get(pk=id)
    except Task.DoesNotExist:
        return Response({'detail': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task)
    return Response(serializer.data)


@api_view(['GET'])
def task_stats(request):
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


class SubTaskPagination(PageNumberPagination):
    page_size = 5


class SubTaskListCreateView(APIView):
    def get(self, request):
        subtasks = SubTask.objects.select_related('task').all().order_by('-created_at')

        task_title = request.query_params.get('task_title')
        if task_title:
            subtasks = subtasks.filter(task__title__icontains=task_title)

        status_param = request.query_params.get('status')
        if status_param:
            subtasks = subtasks.filter(status=status_param)

        paginator = SubTaskPagination()
        result_page = paginator.paginate_queryset(subtasks, request)
        serializer = SubTaskSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    def get_subtask(self, id):
        try:
            return SubTask.objects.get(pk=id)
        except SubTask.DoesNotExist:
            return None

    def get(self, request, id):
        subtask = self.get_subtask(id)
        if subtask is None:
            return Response({'detail': 'SubTask not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data)

    def put(self, request, id):
        subtask = self.get_subtask(id)
        if subtask is None:
            return Response({'detail': 'SubTask not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubTaskCreateSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        subtask = self.get_subtask(id)
        if subtask is None:
            return Response({'detail': 'SubTask not found.'}, status=status.HTTP_404_NOT_FOUND)
        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
