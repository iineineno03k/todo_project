from django.contrib import admin
from .models import Todo

class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'due_date', 'created_at', 'updated_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')
    ordering = ('-priority', 'due_date')

admin.site.register(Todo, TodoAdmin)
