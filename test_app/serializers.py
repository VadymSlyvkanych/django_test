from django.utils import timezone
from rest_framework import serializers

from .models import Category, SubTask, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at']
        read_only_fields = ['id']


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

    def create(self, validated_data):
        if Category.objects.filter(name=validated_data['name']).exists():
            raise serializers.ValidationError(
                {'name': 'Category with this name already exists.'}
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.name)
        if Category.objects.filter(name=name).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError(
                {'name': 'Category with this name already exists.'}
            )
        return super().update(instance, validated_data)


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'categories', 'status', 'deadline', 'created_at', 'subtasks']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'categories', 'status', 'deadline', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError('Deadline cannot be in the past.')
        return value
