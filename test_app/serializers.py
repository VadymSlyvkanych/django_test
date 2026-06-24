import re

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from .models import Category, SubTask, Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'created_at', 'owner']


class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'task', 'status', 'deadline', 'created_at', 'owner']
        read_only_fields = ['id', 'owner']


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_deleted', 'deleted_at']
        read_only_fields = ['is_deleted', 'deleted_at']

    def create(self, validated_data):
        deleted = Category.all_objects.filter(
            name=validated_data['name'], is_deleted=True
        ).first()
        if deleted:
            deleted.is_deleted = False
            deleted.deleted_at = None
            deleted.save(update_fields=['is_deleted', 'deleted_at'])
            return deleted
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.name)
        if Category.all_objects.filter(name=name, is_deleted=True).exists():
            raise serializers.ValidationError(
                {'name': 'Category with this name is deleted.'}
            )
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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already taken.')
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError('Email is required.')
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate_password(self, value):
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError('Password must contain at least one letter.')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Password must contain at least one digit.')
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        data['user'] = user
        return data
