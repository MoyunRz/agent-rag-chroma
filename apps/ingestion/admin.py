from django.contrib import admin

from .models import ChunkRecord, Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    readonly_fields = ['version_number', 'content_hash', 'status', 'chunks_count', 'created_at']
    extra = 0


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'kb', 'mime_type', 'created_at']
    list_filter = ['kb', 'mime_type']
    search_fields = ['title']
    inlines = [DocumentVersionInline]


@admin.register(ChunkRecord)
class ChunkRecordAdmin(admin.ModelAdmin):
    list_display = ['chunk_index', 'version', 'page', 'created_at']
