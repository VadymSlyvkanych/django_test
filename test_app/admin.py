from django.contrib import admin
from django.contrib import messages
from .models import Category, Task, SubTask


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    fields = ['title', 'description', 'status', 'deadline']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_title', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'categories', 'created_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['categories']
    inlines = [SubTaskInline]

    @admin.display(description='Title')
    def short_title(self, obj):
        if len(obj.title) > 10:
            return f'{obj.title[:10]}...'
        return obj.title


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'task', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    actions = ['mark_as_done']

    @admin.action(description='Mark selected subtasks as Done')
    def mark_as_done(self, request, queryset):
        updated = queryset.update(status='done')
        self.message_user(
            request,
            f'{updated} subtask(s) successfully marked as Done.',
            messages.SUCCESS,
        )