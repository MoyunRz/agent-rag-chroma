from django.contrib import admin

from .models import KnowledgeBase


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
